from crafting.recipe import RecipeDatabase
from crafting.gear import GearDatabase
from crafting.environment import Environment
from crafting.action import ActionMapper
import os

from stable_baselines3.common.env_util import make_vec_env
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.ppo_mask import MaskablePPO


class Loader:

    def __init__(self, parent: object = None) -> None:

        assert parent

        self.parent = parent
        self.recipedb = RecipeDatabase()
        self.geardb  = GearDatabase()
        self.modelName = 'ff14crafter'

        self.env = make_vec_env(lambda: Environment(recipedb=self.recipedb, geardb=self.geardb), n_envs=len(ActionMapper._ACTIONS))
        self.model = MaskablePPO(MaskableActorCriticPolicy, self.env, n_steps=10000 // self.env.num_envs) # , learning_rate=1

        if os.path.exists(f'{self.modelName}.zip'):
            self.model.set_parameters(self.modelName)

        self.parent.modelName = self.modelName
        self.parent.env = self.env
        self.parent.model = self.model
