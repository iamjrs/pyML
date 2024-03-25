import json
from os import listdir
from dataclasses import dataclass
import random
from crafting import Schema


@dataclass
class Recipe:
    baseLevel: int
    difficulty: int
    durability: int
    level: int
    maxQuality: int
    progressDivider: int
    progressModifier: int
    qualityDivider: int
    qualityModifier: int
    suggestedControl: int
    suggestedCraftsmanship: int
    stars: int = 0
    category: str = "Random"
    name: str = "Random"


class RecipeSchema(Schema):
    _base = Recipe
    baseLevel = range(1, 90)
    difficulty = range(9, 7480)
    durability = range(35, 80)
    level = range(1, 611)
    maxQuality = range(60, 16156)
    progressDivider = range(50, 180)
    progressModifier = range(80, 100)
    qualityDivider = range(30, 180)
    qualityModifier = range(70, 100)
    suggestedControl = range(11, 2703)
    suggestedCraftsmanship = range(22, 2924)
    stars = range(0, 5)


class RecipeDatabase:
    def __init__(self, dbPath: str = "crafting/recipedb/") -> None:

        self.dbPath = dbPath
        self.db = {}
        self._load()

    def _load(self):
        for file in listdir(self.dbPath):
            with open(self.dbPath + file, "r") as content:
                category = file.split(".")[0]
                self.db[category] = []
                recipes = json.loads(content.read())
                for r in recipes:
                    r["name"] = r["name"]["en"]
                    r = Recipe(category=category, **r)
                    self.db[category].append(r)

    def get(self, name: str) -> Recipe:
        for category in self.db:
            recipes = self.db[category]
            for recipe in recipes:
                if recipe.name == name:
                    return recipe

    def random(self, category: str = None, level: int = None) -> Recipe:
        if not category:
            category = random.choice(list(self.db.keys()))
        recipes = self.db[category]
        if level:
            recipes = [r for r in recipes if r.baseLevel <= level + 5]
        recipe = random.choice(recipes)
        return recipe
