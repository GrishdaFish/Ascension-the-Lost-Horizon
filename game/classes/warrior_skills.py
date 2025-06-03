__author__ = 'GrishdaFish'
from game.classes import skills

# x,y offsets for co-ords next to the player
offsets = [(1, 0), (0, 1), (-1, 0), (0, -1),
           (1, 1), (-1, 1), (-1, -1), (1, -1)]

class WeaponProf(skills.PassiveSkill):
    def __init__(self, name="", owner=None, description="", required_class=None):
        super().__init__(name, owner, description)
        self.required_class = required_class


def whirlwind(gEngine, game, owner):
    if game:
        game.message.message(("%s used whirlwind!"%owner.name))

    else:
        return
