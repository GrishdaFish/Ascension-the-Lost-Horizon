__author__ = 'GrishdaFish'
import toml
import tcod as libtcod

def load_content(path):
    file = open(path).read()
    content = toml.loads(file)
    if content.get('monster'):
        return load_monsters(content.get('monster'))
    if content.get('consumable'):
        return load_consumables(content.get('consumable'))
    if content.get('currency'):
        return load_currency(content.get('currency'))
    if content.get('monster_weapon'):
        return load_monster_weapon(content.get('monster_weapon'))
    if content.get('armor'):
        return load_armor(content.get('armor'))
    if content.get('weapon'):
        return load_weapon(content.get('weapon'))
    if content.get('material'):
        return load_material(content.get('material'))
    if content.get('light_source'):
        return load_light_sources(content.get('light_source'))
    if content.get('ammo'):
        return load_ammo(content.get('ammo'))
    if content.get('spellbook'):
        return load_books(content.get('spellbook'))
    if content.get('spell'):
        return load_spells(content.get('spell'))

def load_monsters(content):
    monster_array = []
    for monster in content:
        m = Monster()
        m.name = monster.get('name')
        m.cell = monster.get('cell')
        m.hp = monster.get('hp')
        m.defense = monster.get('defense')
        m.power = monster.get('power')
        m.type = monster.get('type')
        m.threat_level = monster.get('threat_level')
        m.starting_depth = monster.get('starting_depth')
        m.deepest_depth = monster.get('deepest_depth')
        m.speed = monster.get('speed')
        m.strength = monster.get('strength')
        m.dexterity = monster.get('dexterity')
        m.intelligence = monster.get('intelligence')
        m.defense_bonus = monster.get('defense_bonus')
        m.xp_value = monster.get('xp_reward')
        m.can_equip_gear = monster.get('can_equip_gear')
        m.size = monster.get('size')
        color = monster.get('color')
        m.color = libtcod.Color(color[0], color[1], color[2])
        monster_array.append(m)
    return monster_array


def load_consumables(content):
    consumable_array = []
    for consumable in content:
        c = Consumable()
        c.name = consumable.get('name')
        c.cell = consumable.get('cell')
        c.type = consumable.get('type')
        c.min_effect = consumable.get('min_effect')
        c.max_effect = consumable.get('max_effect')
        c.max_stack = consumable.get('max_stack')
        c.effect_type = consumable.get('effect_type')
        c.additional_effects = consumable.get('additional_effects')
        col = consumable.get('effect_color')
        c.effect_color = libtcod.Color(col[0], col[1], col[2])
        c.range = consumable.get('range')
        c.radius = consumable.get('radius')
        c.max_targets = consumable.get('max_targets')
        col = consumable.get('col')
        c.color = libtcod.Color(col[0], col[1], col[2])
        c.value = consumable.get('value')
        c.stackable = consumable.get('stackable')
        c.level = consumable.get('level')
        consumable_array.append(c)
    return consumable_array

def load_books(content):
    books = []
    for book in content:
        b = Book()
        b.name = book.get('name')
        b.cell = book.get('cell')
        b.type = book.get('type')
        b.starting_spells = book.get('starting_spells')
        b.maximum_spells = book.get('maximum_spells')
        b.max_stacks = book.get('max_stacks')
        b.stackable = book.get('stackable')
        b.value = book.get('value')
        b.level = book.get('level')
        b.specialty = book.get('speciality')
        b.color = book.get('color')
        books.append(b)
    return books


def load_currency(content):
    currency_array = []
    for currency in content:
        c = Currency()
        c.name = currency.get('name')
        c.cell = currency.get('cell')
        c.worth = currency.get('worth')
        c.is_coin = currency.get('is_coin')
        col = currency.get('col')
        c.color = libtcod.Color(col[0], col[1], col[2])
        c.stackable = currency.get('stackable')
        currency_array.append(c)
    return currency_array


def load_monster_weapon(content):
    mon_weap = []
    for weap in content:
        w = MonsterWeapon()
        w.name = weap.get('name')
        w.type = weap.get('type')
        w.subtype = weap.get('subtype')
        w.handed = weap.get('handed')
        w.dual_wield = weap.get('dual_wield')
        w.damage_type = weap.get('damage_type')
        w.damage = weap.get('damage')
        w.accuracy = weap.get('accuracy')
        mon_weap.append(w)
    return mon_weap


def load_armor(content):
    armor = []
    for arm in content:
        a = Armor()
        a.name = arm.get('name')
        a.cell = arm.get('cell')
        a.type = arm.get('type')
        a.location = arm.get('location')
        a.value = arm.get('base_value')
        a.description = arm.get('description')
        a.threat_level = arm.get('threat_level')
        a.allowed_materials = arm.get('allowed_materials')
        a.bonus = arm.get('bonus')
        a.penalty = arm.get('penalty')
        armor.append(a)
    return armor


def load_weapon(content):
    wep = []
    for weap in content:
        w = Weapon()
        w.name = weap.get('name')
        w.cell = weap.get('cell')
        w.type = weap.get('type')
        w.subtype = weap.get('subtype')
        w.handed = weap.get('handed')
        w.dual_wield = weap.get('dual_wield')
        w.damage_type = weap.get("damage_type")
        w.family = weap.get('family')
        w.value = weap.get('base_value')
        w.description = weap.get('description')
        w.threat_level = weap.get('threat_level')
        w.size = weap.get('size')
        w.damage = weap.get('damage')
        w.accuracy = weap.get('accuracy')
        wep.append(w)
    return wep


def load_material(content):
    mat = []
    for material in content:
        m = Material()
        m.name = material.get('name')
        m.price_mod = material.get('price_mod')
        m.rarity = material.get('rarity')
        m.type = material.get('type')
        m.can_be_made_from = material.get('can_be_made_from')
        m.description = material.get('description')
        c = material.get('color')
        m.color = libtcod.Color(c[0], c[1], c[2])
        m.armor_bonus = material.get('armor_bonus')
        m.armor_penalty = material.get('armor_penalty')
        m.weight = material.get('weight')
        m.sharpness = material.get('sharpness')
        m.durability = material.get('durability')
        m.modifier = material.get('modifier')
        mat.append(m)
    return mat


def load_light_sources(content):
    lights = []
    for light in content:
        l = LightSource()
        l.name = light.get('name')
        l.cell = light.get('cell')
        l.max_fuel = light.get('max_fuel')
        c = light.get('color')
        l.color = libtcod.Color(c[0], c[1], c[2])
        c = light.get('effect_color')
        l.effect_color = libtcod.Color(c[0], c[1], c[2])
        l.value = light.get('value')
        l.intensity = light.get('intensity')
        lights.append(l)
    return lights


def load_ammo(content):
    ammos = []
    for ammo in content:
        a = Ammo()
        a.name = ammo.get('name')
        a.cell = ammo.get('cell')
        a.weapon_type = ammo.get('weapon_type')
        a.max_stack = ammo.get('max_stack')
        a.multiplier = ammo.get('multiplier')
        a.col = ammo.get('col')
        a.value = ammo.get('value')
        a.stackable = ammo.get('stackable')
        ammos.append(a)
    return ammos

def load_spells(content):
    spells = []
    for spell in content:
        s = SpellSkills()
        s.name = spell.get("name")
        s.min_effect = spell.get("min_effect")
        s.max_effect = spell.get('max_effect')
        s.radius = spell.get('radius')
        s.num_targets = spell.get('num_targets')
        s.type = spell.get('type')
        s.range = spell.get('range')
        s.effect_per_level = spell.get('effect_per_level')
        s.additional_effect = spell.get('additional_effect')
        s.additional_effect_magnitude = spell.get('additional_effect_magnitude')
        s.magnitude_per_level = spell.get('magnitude_per_level')
        s.spell_fx = spell.get('spell_fx')
        spells.append(s)
    return spells

class Ammo:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.type = "ammo"
        self.weapon_type = ""
        self.max_stack = 0
        self.multiplier = 0
        self.col = [1, 1, 1]
        self.value = 0
        self.stackable = True

class LightSource:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.max_fuel = 0
        self.color = None
        self.effect_color = None
        self.value = None
        self.intensity = 0.0
        self.type = "light_source"

class Consumable:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.type = ""
        self.min_effect = 0
        self.max_effect = 0
        self.effect_type = ""
        self.additional_effects = ""
        self.spell_effect = ""
        self.effect_color = None
        self.range = 0
        self.radius = 0
        self.max_targets = 0
        self.color = None
        self.value = 0
        self.max_stack = 0
        self.stackable = None
        self.level = 0

class Book:
    def __init__(self):
        self.name = ""
        self.cell = ""
        self.type = ""
        self.starting_spells = 0
        self.maximum_spells = 0
        self.max_stacks = 0
        self.stackable = False
        self.value = 0
        self.level = 0
        self.specialty = ''
        self.color = None

class Currency:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.worth = 0
        self.is_coin = False
        self.color = None
        self.type = None
        self.stackable = False


class Weapon:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.min_power = 0
        self.max_power = 0
        self.type = ""
        self.subtype = ""
        self.handed = 0
        self.dual_wield = False
        self.damage_type = ""
        self.color = None
        self.crit_bonus = 0.0
        self.value = 0
        self.threat_level = 0.0
        self.size = None
        self.damage = None
        self.accuracy = 0
        self.family = None
        self.description = None

class Armor:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.type = ""
        self.defense = 0
        self.location = ""
        self.best_defense_type = ""
        self.worst_defense_type = ""
        self.value = 0
        self.threat_level = 0.0
        self.description = ""
        self.allowed_materials = 0
        self.bonus = 0
        self.penalty = 0


class Monster:
    def __init__(self):
        self.name = ''
        self.cell = ''
        self.hp = 0
        self.defense = 0
        self.power = 0
        self.type = ''
        self.threat_level = 0.0
        self.starting_depth = 0
        self.deepest_depth = 0
        self.speed = 0
        self.strength = 0
        self.dexterity = 0
        self.intelligence = 0
        self.color = None
        self.xp_value = 0
        self.size = None
        self.can_equip_gear = False
        self.defense_bonus = 0


class Material:
    def __init__(self):
        self.name = ""
        self.modifier = 0
        self.weight = 0
        self.price_mod = 0.0
        self.hardness = 0
        self.edge = 0
        self.rarity = 0.0
        self.can_be_weapon = None
        self.can_be_armor = None
        self.color = None
        self.armor_bonus = 0
        self.armor_penalty = 0
        self.weight = 0
        self.sharpness = 0
        self.durability = 0
        self.can_be_made_from = 0
        self.type = 0
        self.description = None

class KeyControls:
    def __init__(self):
        self.set_name = ""
        self.key_north = None
        self.key_east = None
        self.key_south = None
        self.key_west = None
        self.key_inventory = None
        self.key_pickup = None
        self.key_equip = None
        self.key_help = None
        self.key_drop = None
        self.key_char = None


class MonsterWeapon:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.subtype = ""
        self.handed = 0
        self.dual_wield = False
        self.damage = None
        self.accuracy = 0
        self.damage_type = ''


class GameOptions:
    def __init__(self):
        self.key_set = ""

class SpellSkills:
    def __init__(self):
        self.name = ""
        self.min_effect = 0
        self.max_effect = 0
        self.radius = 0
        self.num_targets = 0
        self.type = ""
        self.range = 0
        self.effect_per_level = []
        self.additional_effect = []
        self.additional_effect_magnitude = 0
        self.magnitude_per_level = 0
        self.spell_fx = ""