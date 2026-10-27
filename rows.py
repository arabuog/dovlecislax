"""Keep a screen-space row identity instead of selecting the closest fruit anew."""
import numpy as np
from navigation import Action, point


class Row:
    def __init__(self):
        self.line = None
        self.harvested = 0
        self.missing_since = None

    def acquire(self, boxes, width, height):
        if not boxes:
            return None
        seed = min(boxes, key=lambda b: abs(point(b,width,height)[0]-.52)
                   + max(0,.66-point(b,width,height)[1])*.6)
        p = point(seed,width,height)
        # Seed the row through a perspective vanishing point, then fit its fruit.
        a = (p[0]-.52)/max(.1,p[1]-.23)
        self.line = np.array((a, p[0]-a*p[1]))
        members = self.members(boxes,width,height)
        if len(members) >= 3:
            pts = np.array([point(b,width,height) for b in members])
            if np.ptp(pts[:,1]) > .08:
                self.line = np.polyfit(pts[:,1],pts[:,0],1)
        return seed

    def members(self, boxes, width, height):
        if self.line is None:
            return []
        result=[]
        for box in boxes:
            p=point(box,width,height)
            tolerance = max(.012, .035*(p[1]-.23)/.43)
            if abs(p[0]-np.polyval(self.line,p[1])) <= tolerance:
                result.append(box)
        return result

    def observed_shift(self, old_box, new_box, width, height):
        if self.line is not None:
            dx,dy = point(new_box,width,height)-point(old_box,width,height)
            self.line[1] += dx-self.line[0]*dy

    def choose(self, boxes, width, height, now):
        if self.line is None:
            target=self.acquire(boxes,width,height)
        else:
            members=self.members(boxes,width,height)
            target=max(members,key=lambda b: point(b,width,height)[1],default=None)
        if target is None:
            if self.missing_since is None:
                self.missing_since=now
        else:
            self.missing_since=None
        return target

    def finished(self, now):
        return (self.harvested > 0 and self.missing_since is not None
                and now-self.missing_since >= 2.5)


class RowServo:
    def __init__(self, collect_y=.66):
        self.goal=collect_y

    def action(self, position):
        x,y=position
        if abs(x-.52) > .045:
            return Action('d' if x>.52 else 'a', .06)
        if y < self.goal-.035:
            return Action('w', .18 if y<self.goal-.12 else .06)
        if y > self.goal+.07:
            return Action('s', .04)
        return Action('e',.05)

    def observe(self, *_):
        pass
