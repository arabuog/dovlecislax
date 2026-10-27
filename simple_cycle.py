"""Timed W -> E -> rest loop; no detection, screenshots or navigation."""
import math


class Cycle:
    def __init__(self, walk=1.8, rest=7.0, key='e', settle=0., press=.05):
        if not (math.isfinite(walk) and walk > 0 and math.isfinite(rest) and rest >= 0):
            raise ValueError('Durations must be positive and finite')
        if not (math.isfinite(settle) and settle >= 0 and math.isfinite(press) and press > 0):
            raise ValueError('Invalid stop or key press duration')
        self.walk = walk
        self.rest = rest
        self.key = key
        self.settle = settle
        self.press = press
        self.phase = 'idle'
        self.deadline = 0.

    def start(self, now):
        self.phase = 'walk'
        self.deadline = now+self.walk

    def pause(self):
        self.phase = 'idle'

    def start_press(self, now):
        self.phase = 'press'
        self.deadline = now+self.press

    def tick(self, now):
        if self.phase != 'idle' and now >= self.deadline:
            if self.phase == 'walk':
                if self.settle:
                    self.phase = 'settle'
                    self.deadline = now+self.settle
                else:
                    self.start_press(now)
            elif self.phase == 'settle':
                self.start_press(now)
            elif self.phase == 'press':
                self.phase = 'rest'
                self.deadline = now+self.rest
            elif self.phase == 'rest':
                self.phase = 'walk'
                self.deadline = now+self.walk
        return {'walk':'w', 'press':self.key}.get(self.phase)
