__author__ = 'GrishdaFish'
from game.classes import skills


class WeaponProf(skills.PassiveSkill):
    def __init__(self, name="", owner=None, description="", required_class=None):
        super().__init__(name, owner, description)
        self.required_class = required_class

