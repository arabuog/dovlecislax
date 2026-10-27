"""Finite action bursts either after walking or distributed during walking."""
from simple_cycle import Cycle


class RepeatCycle(Cycle):
    def __init__(self, *args, repeats=1, during_walk=False, **kwargs):
        super().__init__(*args, **kwargs)
        if type(repeats) is not int or not 1 <= repeats <= 1000:
            raise ValueError('Invalid repeat count')
        if during_walk and self.walk < repeats*(self.press+.05):
            raise ValueError('Walking interval too short for the requested presses')
        self.repeats = repeats
        self.during_walk = during_walk
        self.sent = 0
        self.press_end = None
        self.next_press = 0
        self.walk_end = 0

    def start(self, now):
        self.sent = 0
        self.press_end = None
        self.next_press = now
        self.walk_end = now+self.walk
        super().start(now)

    def start_press(self, now):
        self.sent += 1
        super().start_press(now)

    def tick(self, now):
        if self.during_walk:
            return self.moving_tick(now)
        if self.phase == 'press' and now >= self.deadline and self.sent < self.repeats:
            self.phase = 'gap'
            self.deadline = now+.1
            return None
        if self.phase == 'gap':
            if now >= self.deadline:
                self.start_press(now)
                return self.key
            return None
        if self.phase == 'rest' and now >= self.deadline:
            self.start(now)
            return 'w'
        return super().tick(now)

    def moving_tick(self, now):
        if self.phase == 'idle':
            return None
        if self.phase == 'rest':
            if now < self.deadline:
                return None
            self.start(now)
        if now >= self.walk_end:
            self.phase = 'rest'
            self.deadline = now+self.rest
            self.press_end = None
            return None
        if self.press_end is not None:
            if now < self.press_end:
                return frozenset(('w',self.key))
            self.press_end = None
            self.next_press = max(self.next_press,now+.05)
            return 'w'  # Guarantee a key-up event between presses, even after lag.
        if self.sent < self.repeats and now >= self.next_press:
            # Never start a press that cannot finish before walking ends.
            if self.walk_end-now >= self.press:
                self.sent += 1
                self.press_end = now+self.press
                spacing = self.walk/self.repeats
                self.next_press = self.walk_end-self.walk+self.sent*spacing
                return frozenset(('w',self.key))
        return 'w'
