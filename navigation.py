"""Screen-space visual servo. No game memory or world coordinates are used."""
from dataclasses import dataclass
import cv2
import numpy as np


def point(box, width, height):
    x, y, w, h = box
    return np.array(((x + w/2)/width, (y+h)/height), dtype=float)


def choose(boxes, width, height, excluded=()):
    candidates = [b for b in boxes
                  if b not in excluded and b[2] >= width*.009
                  and .08 <= point(b, width, height)[0] <= .92]
    if not candidates:
        return None
    # Prefer nearby fruit, including neighbouring rows, rather than a fixed lane.
    return min(candidates, key=lambda b:
               np.linalg.norm((point(b, width, height)-(.52, .66)) * (1, 1.5)))


def follow(previous, current, box, candidates):
    """Match the same fruit after a short movement using forward/backward flow."""
    if not candidates:
        return None
    a = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    x, y, w, h = box
    mask = np.zeros(a.shape, np.uint8)
    mask[max(0,y):y+h, max(0,x):x+w] = 255
    points = cv2.goodFeaturesToTrack(a, 40, .01, 3, mask=mask)
    if points is None or len(points) < 3:
        return None
    nxt, status, _ = cv2.calcOpticalFlowPyrLK(a, b, points, None)
    if nxt is None:
        return None
    back, status_back, _ = cv2.calcOpticalFlowPyrLK(b, a, nxt, None)
    if back is None:
        return None
    valid = ((status.ravel() == 1) & (status_back.ravel() == 1)
             & (np.linalg.norm((back-points).reshape(-1,2), axis=1) < 2))
    if valid.sum() < 3:
        return None
    shift = np.median((nxt-points).reshape(-1,2)[valid], axis=0)
    expected = np.array((x+w/2,y+h/2)) + shift
    best = min(candidates, key=lambda c: np.linalg.norm(
        np.array((c[0]+c[2]/2,c[1]+c[3]/2))-expected))
    distance = np.linalg.norm(np.array((best[0]+best[2]/2,best[1]+best[3]/2))-expected)
    if distance > max(15, w*.6) or not .35 < best[2]*best[3]/(w*h) < 3:
        return None
    return best


@dataclass(frozen=True)
class Action:
    key: str
    seconds: float


class Servo:
    def __init__(self, collect_y=.66):
        self.goal = np.array((.52, collect_y))
        # Target displacement per second of W and D. Updated from observed motion.
        self.matrix = np.array(((0., -.18), (.16, 0.)))

    def action(self, position):
        error = self.goal - np.asarray(position)
        if abs(error[0]) < .035 and abs(error[1]) < .035:
            return Action('e', .05)
        duration = np.linalg.lstsq(self.matrix, error, rcond=None)[0]
        axis = int(np.argmax(np.abs(duration)))
        key = (('w','s'), ('d','a'))[axis][int(duration[axis] < 0)]
        return Action(key, float(np.clip(abs(duration[axis]), .04, .18)))

    def observe(self, before, after, action):
        if action.key not in ('w','s','a','d'):
            return
        delta = np.asarray(after)-np.asarray(before)
        if not np.all(np.isfinite(delta)) or np.linalg.norm(delta) < .002:
            return
        if np.linalg.norm(delta) > .15:
            return  # Likely a bad match or a camera cut.
        axis = int(action.key in ('a','d'))
        sign = -1 if action.key in ('s','a') else 1
        rate = delta / (action.seconds*sign)
        proposal = self.matrix.copy()
        proposal[:,axis] = .7*self.matrix[:,axis] + .3*rate
        if np.linalg.cond(proposal) < 15:
            self.matrix = proposal


class Scan:
    """Bounded search, not proof that the entire world has been cleared."""
    def __init__(self, steps=24):
        self.limit = steps
        self.steps = 0

    def next(self):
        if self.steps >= self.limit:
            return False
        self.steps += 1
        return True

    def reset(self):
        self.steps = 0
