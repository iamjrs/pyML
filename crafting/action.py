from crafting.state import *
from random import random
import numpy as np

from crafting.state import State

RNG_DIVISOR = 2

class Action:

    name: str = "Action"
    durability: int = 10
    successRate: float = 1
    comboAction = None

    def __init__(self, state: State = None) -> None:
        self.state = state
        self.player = self.state.player
        self.recipe = self.state.recipe

        if self.state.history[-1] == self.comboAction:
            self._combo_bonus()

        self.conditions = [
            # self.successRate == 1,
            self.player.level >= self.level,
            self.player.cp >= self.cp,
            self.state.durability > 0,
            not (self.name in self.state.buffs and self.state.buffs[self.name] > 0),
        ]

    def _calculate(self):
        pass

    def _combo_bonus(self):
        pass

    def canUse(self):
        if all(self.conditions):
            return True

    def _use(self):
        return self.state

    def _condition(self):

        excellent_chance = .1 / RNG_DIVISOR
        good_chance = .25 / RNG_DIVISOR

        if self.state.condition == POOR:
            self.state.condition = NORMAL

        elif self.state.condition == NORMAL:
            val = random()
            if val <= excellent_chance:
                self.state.condition = EXCELLENT
            elif val <= good_chance:
                self.state.condition = GOOD

        elif self.state.condition == GOOD:
            self.state.condition = NORMAL

        elif self.state.condition == EXCELLENT:
            self.state.condition = POOR

    def _adjust_buffs(self):
        timedBuffs = [
            'Waste Not',
            'Veneration',
            'Great Strides',
            'Innovation',
            'Final Appraisal',
            'Waste Not II',
            'Muscle Memory',
            'Manipulation',
        ]
        for buff in timedBuffs:
            if self.state.buffs[buff]:
                self.state.buffs[buff] -= 1

    def use(self):

        if self.canUse():

            self.player.cp -= self.cp

            if self.durability:
                durabilityCost = self.durability
                if self.state.buffs['Waste Not'] or self.state.buffs['Waste Not II']:
                    durabilityCost *= .5
                self.state.durability -= durabilityCost
                if self.state.buffs['Manipulation']:
                    self.state.durability += 5

            self._use()
            self.state.history.append(self.__class__)
            self.state.step += 1

            if type(self) not in [FinalAppraisal]:
                self._condition()
                self._adjust_buffs()

        return self.state


class SynthesisAction(Action):
    name: str = "Synthesis Action"
    level: int = 1
    cp: int = 0
    efficiency: float = 1

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.efficiencyMod = self.get_efficiency(self)
        self._calculate(self)

    @staticmethod
    def get_efficiency(self, multiplier: int = 0):

        efficiencyMod = 1
        multiplier = 0

        if type(self) == BasicSynthesis:
            if self.player.level >= 31:
                efficiencyMod += .2

        if self.state.buffs['Veneration']:
            if multiplier:
                multiplier += .5
            else:
                multiplier = 1.5

        if self.state.buffs['Muscle Memory']:
            if multiplier:
                multiplier += 1
            else:
                multiplier = 2

        if multiplier:
            efficiencyMod *= multiplier

        return efficiencyMod

    @staticmethod
    def _calculate(self):
        progress = ( self.player.craftsmanship * 10 ) / self.recipe.progressDivider + 2
        if (self.player.level <= self.recipe.baseLevel):
            progress = (progress * (self.recipe.progressModifier | 100)) / 100
        self.progress = int(progress)
        return self.progress

    @staticmethod
    def _use_action(self, efficiencyMod: float = 0, val: float = random()):

        if val <= self.successRate:
            progress = self.progress * self.efficiency * efficiencyMod
            self.state.progress += int(progress)

            if self.state.buffs['Final Appraisal']:
                if self.state.progress == self.recipe.difficulty:
                    self.state.progress -= 1
                    self.state.buffs['Final Appraisal'] = 0

            self.state.buffs['Muscle Memory'] = 0
        return self.state

    def _use(self):
        self._use_action(self, self.efficiencyMod)
        return self.state


class TouchAction(Action):
    name: str = "Touch Action"
    level: int = 1
    cp: int = 0
    efficiency: float = 1
    innerQuietMax: int = 10

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.efficiencyMod = self.get_efficiency(self)
        self._calculate(self)
        self.conditions.append(
            self.state.quality < self.recipe.maxQuality
        )

    @staticmethod
    def get_efficiency(self, multiplier: int = 0):

        efficiencyMod = 1
        multiplier = 0

        if self.state.buffs['Inner Quiet']:
            efficiencyMod += .1 * self.state.buffs['Inner Quiet']

        if self.state.buffs['Great Strides']:
            if multiplier:
                multiplier += 1
            else:
                multiplier = 2

        if self.state.buffs['Innovation']:
            if multiplier:
                multiplier += .5
            else:
                multiplier = 1.5

        if multiplier:
            efficiencyMod *= multiplier

        efficiencyMod *= CONDITIONS[self.state.condition]
        return efficiencyMod

    @staticmethod
    def _calculate(self):
        quality = ( self.player.control * 10 ) / self.recipe.qualityDivider + 35
        if (self.player.level <= self.recipe.baseLevel):
            quality = (quality * (self.recipe.qualityModifier | 100)) / 100
        self.quality = int(quality)
        return self.quality

    @staticmethod
    def _use_action(self, efficiencyMod: float = 0, val: float = random()):

        if val <= self.successRate:
            quality = self.quality * self.efficiency * efficiencyMod
            self.state.quality += int(quality)

            if self.player.level >= 11:
                if self.state.buffs['Inner Quiet'] < self.innerQuietMax:
                    self.state.buffs['Inner Quiet'] += 1

            self.state.buffs['Great Strides'] = 0
        return self.state
    
    def _use(self):
        self._use_action(self, self.efficiencyMod)
        return self.state



class BasicSynthesis(SynthesisAction):
    name: str = "Basic Synthesis"
    level: int = 1
    cp: int = 0
    efficiency: float = 1


class BasicTouch(TouchAction):
    name: str = "Basic Touch"
    level: int = 5
    cp: int = 18
    efficiency: float = 1


class MastersMend(Action):
    name: str = "Master's Mend"
    level: int = 7
    cp: int = 88
    durability: int = 0

    def _use(self):
        self.state.durability += 30
        return self.state


class HastyTouch(TouchAction):
    name: str = "Hasty Touch"
    level: int = 9
    cp: int = 0
    efficiency: float = 1
    successRate: float = .6 / RNG_DIVISOR

    # def __init__(self, state: State = None) -> None:
    #     super().__init__(state)
    #     for action in QualityActions:
    #         if action != HastyTouch:
    #             if action(self.state).canUse():
    #                 self.conditions.append(False)
    #                 return


class RapidSynthesis(SynthesisAction):
    name: str = "Rapid Synthesis"
    level: int = 9
    cp: int = 0
    efficiency: float = 2.5
    successRate: float = .5 / RNG_DIVISOR

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        if self.player.level >= 63:
            self.efficiency = 5


class Observe(Action):
    name: str = "Observe"
    level: int = 13
    cp: int = 7
    durability: int = 0

    # def __init__(self, state: State = None) -> None:
    #     super().__init__(state)
    #     self.conditions.append(
    #         self.state.condition == POOR
    #     )

class TricksOfTheTrade(Action):
    name: str = "Tricks of the Trade"
    level: int = 13
    cp: int = 0
    durability: int = 0

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.condition in [GOOD, EXCELLENT]
        )

    def _use(self):
        self.player.cp += 20
        return self.state


class WasteNot(Action):
    name: str = "Waste Not"
    level: int = 15
    cp: int = 56
    durability: int = 0

    def _use(self):
        self.state.buffs['Waste Not'] = 5
        self.state.buffs['Waste Not II'] = 0
        return self.state


class Veneration(Action):
    name: str = "Veneration"
    level: int = 15
    cp: int = 18
    durability: int = 0

    def _use(self):
        self.state.buffs['Veneration'] = 5
        return self.state
    

class StandardTouch(TouchAction):
    name: str = "Standard Touch"
    level: int = 18
    cp: int = 32
    efficiency: float = 1.25
    comboAction = BasicTouch

    def _combo_bonus(self):
        self.cp = 18


class GreatStrides(Action):
    name: str = "Great Strides"
    level: int = 21
    cp: int = 32
    durability: int = 0

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.quality < self.recipe.maxQuality
        )

    def _use(self):
        self.state.buffs['Great Strides'] = 4
        return self.state


class Innovation(Action):
    name: str = "Innovation"
    level: int = 26
    cp: int = 18
    durability: int = 0
 
    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.quality < self.recipe.maxQuality
        )

    def _use(self):
        self.state.buffs['Innovation'] = 5


class FinalAppraisal(Action):
    name: str = "Final Appraisal"
    level: int = 42
    cp: int = 1
    durability: int = 0

    # def __init__(self, state: State = None) -> None:
    #     super().__init__(state)
    #     self.conditions.append(False)

    def _use(self):
        self.state.buffs['Final Appraisal'] = 5
        return self.state


class WasteNotII(Action):
    name: str = "Waste Not II"
    level: int = 47
    cp: int = 98
    durability: int = 0

    def _use(self):
        self.state.buffs['Waste Not II'] = 9
        self.state.buffs['Waste Not'] = 0
        return self.state


class ByregotsBlessing(TouchAction):
    name: str = "Byregot's Blessing"
    level: int = 50
    cp: int = 24
    efficiency: float = 1

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.buffs['Inner Quiet'] > 0
        )
        self.efficiencyMod = 1
        multiplier = 0
        self.efficiency += .2 * self.state.buffs['Inner Quiet']
        
        if self.state.buffs['Inner Quiet']:
            self.efficiencyMod += .1 * self.state.buffs['Inner Quiet']

        if self.state.buffs['Great Strides']:
            if multiplier:
                multiplier += 1
            else:
                multiplier = 2

        if self.state.buffs['Innovation']:
            if multiplier:
                multiplier += .5
            else:
                multiplier = 1.5

        if multiplier:
            self.efficiencyMod *= multiplier

        self.efficiencyMod *= CONDITIONS[self.state.condition]

    def _use(self):
        val = random()
        if val <= self.successRate:
            quality = self.quality * self.efficiency * self.efficiencyMod
            self.state.quality += int(quality)
            self.state.buffs['Great Strides'] = 0
            self.state.buffs["Inner Quiet"] = 0
        return self.state


class PreciseTouch(TouchAction):
    name: str = "Precise Touch"
    level: int = 53
    cp: int = 18
    efficiency: float = 1.5

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.condition in [GOOD, EXCELLENT]
        )



class MuscleMemory(SynthesisAction):
    name: str = "Muscle Memory"
    level: int = 54
    cp: int = 6
    efficiency: float = 3

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.step == 1
        )

    def _use(self):
        val = random()
        if val <= self.successRate:
            progress = self.progress * self.efficiency * self.efficiencyMod
            self.state.progress += int(progress)
            
            if self.state.buffs['Final Appraisal']:
                if self.state.progress == self.recipe.difficulty:
                    self.state.progress -= 1
                    self.state.buffs['Final Appraisal'] = 0

            self.state.buffs['Muscle Memory'] = 6
        return self.state


class CarefulSynthesis(SynthesisAction):
    name: str = "Careful Synthesis"
    level: int = 62
    cp: int = 7
    efficiency: float = 1.5

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        if self.player.level >= 82:
            self.efficiency = 1.8


class Manipulation(Action):
    name: str = "Manipulation"
    level: int = 65
    cp: int = 96
    durability: int = 0

    def _use(self):
        self.state.buffs['Manipulation'] = 9
        return self.state


class PrudentTouch(TouchAction):
    name: str = "Prudent Touch"
    level: int = 66
    cp: int = 25
    efficiency: float = 1
    durability: int = 5

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.extend([
            self.state.buffs['Waste Not'] == 0,
            self.state.buffs['Waste Not II'] == 0
        ])


class FocusedSynthesis(SynthesisAction):
    name: str = "Focused Synthesis"
    level: int = 67
    cp: int = 5
    efficiency: float = 2
    successRate: float = .5 / RNG_DIVISOR
    comboAction = Observe

    # def __init__(self, state: State = None) -> None:
    #     super().__init__(state)
    #     self.conditions.append(
    #         self.successRate == 1
    #     )

    def _combo_bonus(self):
        self.successRate = 1


class FocusedTouch(TouchAction):
    name: str = "Focused Touch"
    level: int = 68
    cp: int = 18
    efficiency: float = 1.5
    successRate: float = .5 / RNG_DIVISOR
    comboAction = Observe

    # def __init__(self, state: State = None) -> None:
    #     super().__init__(state)
    #     self.conditions.append(
    #         self.successRate == 1
    #     )

    def _combo_bonus(self):
        self.successRate = 1


class Reflect(TouchAction):
    name: str = "Reflect"
    level: int = 69
    cp: int = 6
    efficiency: float = 1

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.step == 1
        )


class PreparatoryTouch(TouchAction):
    name: str = "Preparatory Touch"
    level: int = 71
    cp: int = 40
    efficiency: float = 2
    durability: int = 20


class Groundwork(SynthesisAction):
    name: str = "Groundwork"
    level: int = 72
    cp: int = 18
    efficiency: float = 3
    durability: int = 20

    def __init__(self, state: State = None) -> None:
        super().__init__(state)

        if self.player.level >= 86:
            self.efficiency = 3.6

        if self.state.durability < self.durability:
            self.efficiency *= .5


class DelicateSynthesis(Action):
    name: str = "Delicate Synthesis"
    level: int = 76
    cp: int = 32
    efficiency: float = 1
    innerQuietMax: int = 10

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.synthMod = SynthesisAction.get_efficiency(self)
        self.touchMod = TouchAction.get_efficiency(self)
        self.progress = SynthesisAction._calculate(self)
        self.quality = TouchAction._calculate(self)

    def _use(self):
        val = random()
        SynthesisAction._use_action(self, self.synthMod, val=val)
        TouchAction._use_action(self, self.touchMod, val=val)
        return self.state


class IntensiveSynthesis(SynthesisAction):
    name: str = "Intensive Synthesis"
    level: int = 78
    cp: int = 6
    efficiency: float = 4

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.condition in [GOOD, EXCELLENT]
        )


class TrainedEye(Action):
    name: str = "Trained Eye"
    level: int = 80
    cp: int = 250
    efficiency: float = 1
    durability: int = 0

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.extend([
            self.state.step == 1,
            self.recipe.baseLevel <= self.player.level - 10
        ])

    def _use(self):
        self.state.quality = self.recipe.maxQuality
        return self.state


class AdvancedTouch(TouchAction):
    name: str = "Advanced Touch"
    level: int = 84
    cp: int = 46
    efficiency: float = 1.5
    comboAction = StandardTouch

    def _combo_bonus(self):
        self.cp = 18


class PrudentSynthesis(SynthesisAction):
    name: str = "Prudent Synthesis"
    level: int = 88
    cp: int = 18
    efficiency: float = 1.8
    durability: int = 5

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.extend([
            self.state.buffs['Waste Not'] == 0,
            self.state.buffs['Waste Not II'] == 0
        ])


class TrainedFinesse(TouchAction):
    name: str = "Trained Finesse"
    level: int = 90
    cp: int = 32
    efficiency: float = 1
    durability: int = 0

    def __init__(self, state: State = None) -> None:
        super().__init__(state)
        self.conditions.append(
            self.state.buffs['Inner Quiet'] == 10
        )


QualityActions = [
    BasicTouch,
    HastyTouch,
    StandardTouch,
    ByregotsBlessing,
    PreciseTouch,
    PrudentTouch,
    FocusedTouch,
    Reflect,
    PreparatoryTouch,
    DelicateSynthesis,
    TrainedEye,
    AdvancedTouch,
    TrainedFinesse,
]


class ActionMapper:

    _ACTIONS = [
        BasicSynthesis,
        BasicTouch,
        MastersMend,
        HastyTouch,
        RapidSynthesis,
        Observe,
        TricksOfTheTrade,
        WasteNot,
        Veneration,
        StandardTouch,
        GreatStrides,
        Innovation,
        FinalAppraisal,
        WasteNotII,
        ByregotsBlessing,
        PreciseTouch,
        MuscleMemory,
        CarefulSynthesis,
        Manipulation,
        PrudentTouch,
        FocusedTouch,
        FocusedSynthesis,
        Reflect,
        PreparatoryTouch,
        Groundwork,
        DelicateSynthesis,
        IntensiveSynthesis,
        TrainedEye,
        AdvancedTouch,
        PrudentSynthesis,
        TrainedFinesse,
    ]

    def __init__(self, state: State = None) -> None:
        self.state = state

    def get(self, actionVal: np.array = None):
        _ACTIONS = [x for x in self._ACTIONS if x(self.state).canUse()]
        actionVal = actionVal[0]
        actionIndex = round( actionVal * ( len(_ACTIONS) - 1 ) )
        action = _ACTIONS[actionIndex]
        return action

    def get_mask(self) -> list:
        valid_actions = []
        for a in self._ACTIONS:
            if a(self.state).canUse():
                valid_actions.append(1)
            else:
                valid_actions.append(0)
        return valid_actions