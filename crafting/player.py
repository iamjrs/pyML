from dataclasses import dataclass
from crafting import Schema


@dataclass
class Player:
    level: int = 1
    craftsmanship: int = 0
    control: int = 0
    cp: int = 0

    def update(self, stats: dict = None):
        for stat in stats:
            setattr(self, stat, stats[stat])
        self.cp += 180

class PlayerSchema(Schema):
    _base = Player
    level = range(1, 90)
    craftsmanship = range(1, 4000)
    control = range(1, 4000)
    cp = range(0, 600)