from pgcooldown import Cooldown

from .textlabel import TextLabel


class CountdownLabel(TextLabel):
    def __init__(self, count, pos, style, *groups):
        super().__init__('', pos, style, *groups)

        self.count = count + 1
        self.countdown = iter(reversed(range(self.count)))
        self.cooldown = Cooldown(1, cold=True)

    def reset(self, *groups):
        self.countdown = iter(reversed(range(self.count)))
        self.text = next(self.countdown)
        self.cooldown.reset()
        self.add(*groups)

    def update(self, dt):
        super().update(dt)
        if self.cooldown.cold():
            self.cooldown.reset()
            try:
                self.text = next(self.countdown)
            except StopIteration:
                self.kill()
                self.countdown = None

    def __bool__(self):
        return self.countdown is not None
