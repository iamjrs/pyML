from crafting.recipe import Recipe
from crafting.player import Player
from crafting import Schema


NORMAL = 1
GOOD = 2
EXCELLENT = 3
POOR = 4

CONDITIONS = {
    NORMAL: 1, 
    GOOD: 1.5, 
    EXCELLENT: 4,
    POOR: 0.25
}

UNCONDITIONS = {
    NORMAL: 'NORMAL', 
    GOOD: 'GOOD', 
    EXCELLENT: 'EXCELLENT',
    POOR: 'POOR'
}

class State:

    def __init__(
        self,
        player: Player = None,
        recipe: Recipe = None,
        step: int = 1,
        durability: int = 40,
        progress: int = 0,
        quality: int = 0,
        condition: int = NORMAL,
        buffs: list = [],
    ) -> None:

        # control 2703
        # craftsmanship 2924

        self.player = player
        self.recipe = recipe

        self.step = step
        self._durability = recipe.durability
        self._progress = progress
        self._quality = quality
        self.condition = condition

        self.history = [None]

        buffNames = [
            'Inner Quiet',
            'Waste Not',
            'Veneration',
            'Great Strides',
            'Innovation',
            'Final Appraisal',
            'Waste Not II',
            'Muscle Memory',
            'Manipulation',
        ]

        if not buffs:
            buffs = [0] * len(buffNames)

        self.buffs = dict( zip(buffNames, buffs) )


    @property
    def progress(self):
        return self._progress
    @progress.setter
    def progress(self, value):
        value = max([value, 0])
        value = min([value, self.recipe.difficulty])
        self._progress = value
        return self._progress

    @property
    def quality(self):
        return self._quality
    @quality.setter
    def quality(self, value):
        value = max([value, 0])
        value = min([value, self.recipe.maxQuality])
        self._quality = value
        return self._quality

    @property
    def durability(self):
        return self._durability
    @durability.setter
    def durability(self, value):
        value = max([value, 0])
        value = min([value, self.recipe.durability])
        self._durability = value
        return self._durability


    def __repr__(self) -> str:
        s = f'''[{self.recipe.name} Lv. {self.recipe.baseLevel} ({self.recipe.level})]
Step:         {str(self.step)}
Progress:     {str(self.progress)} / {str(self.recipe.difficulty)}
Quality:      {str(self.quality)} / {str(self.recipe.maxQuality)}
Durability:   {str(self.durability)} / {str(self.recipe.durability)}
CP:           {str(self.player.cp)}
Condition:    {UNCONDITIONS[self.condition]}
Buffs:
'''
        for buff in self.buffs:
            if self.buffs[buff]:
                s += f'- {buff}: {str(self.buffs[buff])}\n'

        return s


class StateSchema(Schema):
    _base = State
    step = range(1, 1000)
    durability = range(0, 80)
    progress = range(0, 7480)
    quality = range(0, 16156)
    condition = range(1, 4)