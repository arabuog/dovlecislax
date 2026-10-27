"""Timed W -> E -> rest loop; no detection, screenshots or navigation."""
import math


class Cycle:
    def __init__(self, walk=1.8, rest=7.0):
        if not all(math.isfinite(x) and x > 0 for x in (walk,rest)):
            raise ValueError('Durations must be positive and finite')
        self.walk = walk
        self.rest = rest
        self.phase = 'idle'
        self.deadline = 0.

    def start(self, now):
        self.phase = 'walk'
        self.deadline = now+self.walk

    def pause(self):
        self.phase = 'idle'

    def tick(self, now):
        if self.phase != 'idle' and now >= self.deadline:
            if self.phase == 'walk':
                self.phase = 'press'
                self.deadline = now+.05
            elif self.phase == 'press':
                self.phase = 'rest'
                self.deadline = now+self.rest
            elif self.phase == 'rest':
                self.phase = 'walk'
                self.deadline = now+self.walk
        return {'walk':'w', 'press':'e'}.get(self.phase)
