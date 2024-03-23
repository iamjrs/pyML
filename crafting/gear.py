from dataclasses import dataclass
import random
import json


class Gear:

    control: int = 0
    craftsmanship: int = 0
    cp: int = 0

    def __init__(self, data: dict = None) -> None:

        self.name: str = data['Name']
        self.level: int = data['LevelEquip']
        self.job: str = data['ClassJobCategory']['Name']
        self.slotId: int = data['EquipSlotCategory']['ID']
        self.slotName: str = ''

        for slot in data['EquipSlotCategory']:
            if slot != 'ID':
                if data['EquipSlotCategory'][slot] > 0:
                    if 'Finger' in slot:
                        slot = 'Finger'
                    self.slotName = slot
                    break

        for stat in data['Stats']:
            if stat in ['Craftsmanship', 'Control', 'CP']:
                setattr(self, stat.lower(), data['Stats'][stat]['NQ'])



class GearDatabase:

    def __init__(self, dbPath: str = 'C:\\Users\\jschm\\Documents\\pyML\\crafting\\geardb.json') -> None:

        self.slots = {
            "Body": 4,
            "Ears": 9,
            "Feet": 8,
            "Finger": 12,
            "Gloves": 5,
            "Head": 3,
            "Legs": 7,
            "MainHand": 1,
            "Neck": 10,
            "OffHand": 2,
            # "SoulCrystal": 0,
            # "Waist": 0,
            "Wrists": 11
        }

        self.dbPath = dbPath
        self.db = []
        self._load()

    def _load(self):
        with open(self.dbPath, 'r') as f:
            db = json.loads(f.read())
        for item in db:
            gear = Gear(item)
            self.db.append(gear)
        return self.db

    def get(self, name: str) -> Gear:
        for gear in self.db:
            if gear.name == name:
                return gear

    def random(self, level: int = None, slotName: str = None, job: str = None) -> Gear:
        gears = self.db
        if level:
            gears = [g for g in gears if g.level <= level]
        if slotName:
            gears = [g for g in gears if g.slotName == slotName]
        if job:
            gears = [g for g in gears if job in g.job or g.job == 'All Classes']
        if gears:
            gear = random.choice(gears)
            return gear

    def random_set(self, level: int = None, job: str = None):
        gearset = []
        for slot in self.slots:
            gear = self.random(level=level, slotName=slot, job=job)
            gearset.append(gear)
            if slot == 'Finger':
                gear = self.random(level=level, slotName=slot, job=job)
                gearset.append(gear)
        return gearset

    def random_stats(self, level: int = None, job: str = None):
        gear = self.random_set(level=level, job=job)
        stats = {'craftsmanship': 0, 'control': 0, 'cp': 0}
        for stat in stats:
            stats[stat] += sum([getattr(g, stat) for g in gear if hasattr(g, stat)])
        return stats


if __name__ == "__main__":

    geardb = GearDatabase()
    stats = geardb.random_stats(level=1)

    gear = geardb.random_set()
    for g in gear:
        print(g)
