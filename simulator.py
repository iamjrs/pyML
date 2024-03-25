from crafting.observation import Observation
from crafting.action import ActionMapper, Manipulation
from crafting.environment import Environment
from crafting.player import Player
from crafting.recipe import Recipe, RecipeDatabase
from crafting.state import State
from crafting.gear import GearDatabase
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.ppo import PPO
from sb3_contrib.common.wrappers import ActionMasker
import os


class Simulator:

    def __init__(self, modelPath: str = "ff14crafter.zip") -> None:
        self.modelPath = modelPath
        self.hasManipulation = False
        self.recipedb = RecipeDatabase()
        self.geardb = GearDatabase()
        self.load()

    def load(self) -> MaskablePPO:
        self.env = Environment(recipedb=self.recipedb, geardb=self.geardb)
        self.env = ActionMasker(self.env, self.env.action_masks)
        if os.path.exists(self.modelPath):
            self.model = MaskablePPO.load(self.modelPath, self.env)
        else:
            self.model = MaskablePPO(MaskableActorCriticPolicy, self.env)
        return True

    def _predict(self):
        masks = ActionMapper(self.state).get_mask()
        _index = masks[ActionMapper._ACTIONS.index(Manipulation)]
        masks[_index] = masks[_index] & self.hasManipulation
        obs = Observation(self.state).normalize()
        action, _states = self.model.predict(
            observation=obs, action_masks=masks, deterministic=True
        )
        result = ActionMapper._ACTIONS[action]
        return result

    def predict(self, player):
        self.get_state_from_player(player)
        return self._predict()

    def get_state_from_player(self, player):

        if player.action("Manipulation").canUse():
            self.hasManipulation = True
        else:
            self.hasManipulation = False

        p = Player(
            level=player.level,
            craftsmanship=player.gearCraftsmanship,
            control=player.gearControl,
            cp=player.craftPoints,
        )

        r = self.recipedb.get(player.craftItemName)
        self.state = State(p, r)

        if player.craftState in [3, 6]:
            self.state.quality = player.craftQuality

        if player.craftState in [9, 10]:

            self.state.step = player.craftStep
            self.state.progress = player.craftProgress
            self.state.quality = player.craftQuality
            self.state.durability = player.craftDurability
            self.state.condition = player.craftCondition

            for action in ActionMapper._ACTIONS:
                if action.name == player.craftLastAction:
                    self.state.history.append(action)

        for buff in self.state.buffs:
            status = player.status(buff)
            if status:
                self.state.buffs[buff] = status.procChance

        return self.state
