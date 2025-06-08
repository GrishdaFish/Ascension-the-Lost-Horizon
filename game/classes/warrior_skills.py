__author__ = 'GrishdaFish'
from game.classes import skills

# x,y offsets for co-ords next to the player
offsets = [(1, 0), (0, 1), (-1, 0), (0, -1),
           (1, 1), (-1, 1), (-1, -1), (1, -1)]

class WeaponProf(skills.PassiveSkill):
    def __init__(self, name="", owner=None, description="", required_class=None):
        name = name + " proficiency"
        super().__init__(name, owner, description)
        self.required_class = required_class

def setup_warrior_skills(game, owner):
    warrior_skills = []
    warrior_skills_dict = {}

    ww = skills.CooldownSkill("Whirlwind", owner, "Whirlwind skill", 3, whirlwind, game, game.gEngine, "W")
    warrior_skills.append(ww)
    warrior_skills_dict.update({ww.name: ww})

    ww = skills.ResourceSkill("Bash", owner, "Bash skill", 3, bash, game, game.gEngine, "B")
    warrior_skills.append(ww)
    warrior_skills_dict.update({ww.name: ww})

    return warrior_skills, warrior_skills_dict

def whirlwind(gEngine, game, owner):
    if game:
        game.message.message(("%s used whirlwind!"%owner.name))
        return True
    else:
        return False

def bash(gEngine, game, owner):
    if game:
        game.message.message(("%s used bash!"%owner.name))
        return True
    else:
        return False