"""Conservative visual disappearance check, not a ticket/reward verifier."""
import math


class Collection:
    def __init__(self, box, now, wait=9.0, timeout=18.0):
        self.box = box
        self.started = now
        self.wait = wait
        self.timeout = max(timeout, wait + 3)
        self.absent_since = None

    def update(self, boxes, now):
        x, y, w, h = self.box
        cx, cy = x + w / 2, y + h / 2
        # Match within the original footprint. Camera changes/occlusion can
        # still look like disappearance, so this does not prove reward receipt.
        present = any(math.hypot(bx+bw/2-cx, by+bh/2-cy) < max(w, h) * .7
                      for bx, by, bw, bh in boxes)
        if now - self.started < self.wait:
            self.absent_since = None
            return 'waiting'
        if present:
            self.absent_since = None
        elif self.absent_since is None:
            self.absent_since = now
        elif now - self.absent_since >= 1:
            return 'disappeared'
        if now - self.started >= self.timeout:
            return 'timeout'
        return 'waiting'
