__author__ = 'GrishdaFish'
def is_equipment(item):
    if item:
        if item.item.equipment:
            return True
    return False
def is_weapon(item, owner):
    if item: return owner.fighter.gear.is_weapon(item)
    return None

def is_two_hander(item, owner):
    if item: return owner.fighter.gear.is_two_hander(item)
    return None

def is_shield(item, owner):
    if item: return owner.fighter.gear.is_shield(item)
    return None

def is_armor(item, owner):
    if item: return owner.fighter.gear.is_armor(item)
    return None

def is_light(item, owner):
    if item: return owner.fighter.gear.is_light(item)
    return None
