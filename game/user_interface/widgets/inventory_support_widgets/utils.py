__author__ = 'GrishdaFish'
import tcod as libtcod

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

def get_fuel_color(equip):
    f = equip.item.equipment.fuel
    mf = equip.item.equipment.max_fuel
    if f <= 0:
        f = 1
    perc = f / mf
    if perc >= 0.51:
        color = libtcod.green
    elif perc >= 0.25 and perc <= 50:
        color = libtcod.yellow
    else:
        color = libtcod.red
    return color