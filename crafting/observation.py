from crafting.player import PlayerSchema
from crafting.recipe import RecipeSchema
from crafting.state import State, StateSchema
from crafting.action import *
import numpy as np
from copy import copy


class Observation:
    def __init__(
        self,
        state: State = None,
    ) -> None:
        self.state = state
        self.player = self.state.player
        self.recipe = self.state.recipe

    def normalize(self) -> np.array:
        obs = [
            PlayerSchema.normalize("level", self.player.level),
            PlayerSchema.normalize("craftsmanship", self.player.craftsmanship),
            PlayerSchema.normalize("control", self.player.control),
            PlayerSchema.normalize("cp", self.player.cp),
            RecipeSchema.normalize("baseLevel", self.recipe.baseLevel),
            RecipeSchema.normalize("difficulty", self.recipe.difficulty),
            RecipeSchema.normalize("durability", self.recipe.durability),
            RecipeSchema.normalize("level", self.recipe.level),
            RecipeSchema.normalize("maxQuality", self.recipe.maxQuality),
            RecipeSchema.normalize("progressDivider", self.recipe.progressDivider),
            RecipeSchema.normalize("progressModifier", self.recipe.progressModifier),
            RecipeSchema.normalize("qualityDivider", self.recipe.qualityDivider),
            RecipeSchema.normalize("qualityModifier", self.recipe.qualityModifier),
            RecipeSchema.normalize("suggestedControl", self.recipe.suggestedControl),
            RecipeSchema.normalize(
                "suggestedCraftsmanship", self.recipe.suggestedCraftsmanship
            ),
            RecipeSchema.normalize("stars", self.recipe.stars),
            StateSchema.normalize("step", self.state.step),
            StateSchema.normalize("durability", self.state.durability),
            StateSchema.normalize("progress", self.state.progress),
            StateSchema.normalize("quality", self.state.quality),
            StateSchema.normalize("condition", self.state.condition),
        ]

        buffRanges = {
            "Inner Quiet": range(0, 11),
            "Waste Not": range(0, 4),
            "Veneration": range(0, 4),
            "Great Strides": range(0, 3),
            "Innovation": range(0, 4),
            "Final Appraisal": range(0, 5),
            "Waste Not II": range(0, 8),
            "Muscle Memory": range(0, 5),
            "Manipulation": range(0, 8),
        }

        for buff in self.state.buffs:
            stacks = self.state.buffs[buff]
            buffRange = buffRanges[buff]
            normVal = stacks / buffRange.stop * 2 - 1
            obs.append(normVal)

        for action in ActionMapper._ACTIONS:
            if action.comboAction:
                val = -1
                if action.comboAction == self.state.history[-1]:
                    val = 1
                obs.append(val)

        return np.array(obs, dtype=np.float64)
