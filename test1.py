from crafting.player import PlayerSchema
from crafting.recipe import RecipeDatabase
from crafting.state import State
from crafting.action import *
from crafting.observation import Observation


player = Player(level=65, craftsmanship=1000, control=1000, cp=350)

recipe = RecipeDatabase().get("Steppe Serge")

actions = [
    CarefulSynthesis,
    AdvancedTouch,
    StandardTouch,
]

state = State(player, recipe)

print(state)

for a in actions:
    print(a.name)
    a(state).use()
    print(state)

print(player)
