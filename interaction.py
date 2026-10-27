"""Separate seeing a target from being visually close enough to interact."""
from navigation import Action, point


class Interaction:
    def __init__(self, min_width=.055, min_height=.03, cooldown=9):
        self.min_width = min_width
        self.min_height = min_height
        self.cooldown = cooldown
        self.last_press = None
        self.stable_since = None
        self.forward_progress = 0.

    def new_target(self):
        self.stable_since = None
        self.forward_progress = 0.

    def observe_forward(self, before, after, width, height):
        # Called only for a matched target after an actual forward command.
        dy = point(after,width,height)[1]-point(before,width,height)[1]
        growth = (after[2]-before[2])/width
        if 0 < dy < .08:
            self.forward_progress += dy
        if 0 < growth < .03:
            self.forward_progress += growth

    def guard(self, requested, box, width, height, now):
        if requested.key != 'e':
            self.stable_since = None
            return requested
        if box[2]/width < self.min_width or box[3]/height < self.min_height:
            self.stable_since = None
            return Action('w', .06)
        if self.last_press is not None:
            if now-self.last_press < self.cooldown:
                return Action('wait', .05)
        if self.forward_progress < .015:
            self.stable_since = None
            return Action('w', .06)
        if self.stable_since is None:
            self.stable_since = now
        if now-self.stable_since < .35:
            return Action('wait', .05)
        return requested

    def fired(self, now):
        self.last_press = now
        self.stable_since = None
        self.forward_progress = 0.
