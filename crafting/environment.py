from gymnasium import spaces
import gymnasium as gym
import numpy as np

from crafting.player import *
from crafting.recipe import *
from crafting.state import *
from crafting.observation import *
from crafting.action import *
from crafting.gear import *
from copy import copy


class Environment(gym.Env):

    def __init__(
        self,
        state: State = None,
        recipedb: RecipeDatabase = None,
        geardb: GearDatabase = None,
    ):
        super().__init__()

        self.init_state = None
        self.recipedb = recipedb
        self.geardb = geardb

        if not recipedb:
            self.recipedb = RecipeDatabase()

        if not geardb:
            self.geardb = GearDatabase()

        if state:
            self.init_state = copy(state)
            self.player = state.player
            self.recipe = state.recipe
            self.state = State(self.player, self.recipe)

        else:
            self.player = PlayerSchema.sample()
            stats = self.geardb.random_stats(level=self.player.level)
            self.player.update(stats)
            self.recipe = self.recipedb.random(level=self.player.level)
            self.state = State(self.player, self.recipe)

        obs = Observation(self.state).normalize()
        self.action_space = spaces.Discrete(len(ActionMapper._ACTIONS))
        self.observation_space = spaces.Box(
            low=-1, high=1, shape=(len(obs),), dtype=np.float64
        )

    def step(self, action):

        assert self.action_space.contains(action), action

        reward = 0
        terminated = False
        truncated = False
        info = {}

        ActionClass = ActionMapper._ACTIONS[action]
        Action = ActionClass(self.state)
        Action.use()

        if self.state.progress == self.recipe.difficulty:
            terminated = True
            reward = self.state.quality / self.recipe.maxQuality

        elif not any(ActionMapper(self.state).get_mask()):
            truncated = True
            reward = -1

        obs = Observation(self.state).normalize()

        return obs, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):

        if self.init_state:
            state = copy(self.init_state)
            self.player = state.player
            self.recipe = state.recipe
        else:
            self.player = PlayerSchema.sample()
            stats = self.geardb.random_stats(level=self.player.level)
            self.player.update(stats)
            self.recipe = self.recipedb.random(level=self.player.level)

        self.state = State(self.player, self.recipe)
        obs = Observation(self.state).normalize()
        return obs, {}

    def action_masks(self, env: gym.Env = None):
        if not env:
            env = self
        return ActionMapper(env.state).get_mask()
