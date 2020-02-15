import os

from game.object.object import *
from game.object.item import *
from game.spells import spells
from game.object.misc import *
#from game.spells.spells import *
from game import combat
from game import content_parser
from gEngine import gEngine, custom_font
from game.object.effects import Effect


class GameObjects:
    def __init__(self):
        self.threat_list = []
        self.scrolls = []
        self.potions = []
        self.weapon_mat_rarity = {}
        self.armor_mat_rarity = {}
        self.weapon_mats = []
        self.armor_mats = []
        self.monsters = []  # content[0]
        self.equipment = []  # content[1]
        self.consumables = []  # content[2]
        self.materials = []  # content[3]
        self.ammo = []
        self.currency = []
        self.armor = []
        self.weapons = []
        self.ranged_weapons = []
        self.melee_weapons = []
        self.monster_weapons = []
        self.light_sources = []
        self.load_content()
        # Need to sort all of the different content
        # for the object builders
        self.sort_threat_levels()
        self.sort_consumables()
        self.sort_materials()

    def load_content(self):
        """
        Calls the content parser to load all of the items from disk
        :return:
        """
        # if gEngine.RELEASE:
        #     path = getattr(sys, "_MEIPASS", ".")
        # else:
        #     path = sys.path[0]
        path = os.path.abspath('.')
        self.monsters = content_parser.load_content(os.path.join(path, 'content', 'actors', 'monsters.toml'))
        self.consumables = content_parser.load_content(
            os.path.join(path, 'content', 'items', 'consumables.toml'))
        self.currency = content_parser.load_content(os.path.join(path, 'content', 'items', 'currency.toml'))
        self.materials = content_parser.load_content(os.path.join(path, 'content', 'items', 'materials.toml'))
        self.monster_weapons = content_parser.load_content(
            os.path.join(path, 'content', 'items', 'monster_weapons.toml'))
        self.armor = content_parser.load_content(os.path.join(path, 'content', 'items', 'armor.toml'))
        self.weapons = content_parser.load_content(os.path.join(path, 'content', 'items', 'weapons.toml'))
        self.light_sources = content_parser.load_content(os.path.join(path, 'content', 'items', 'light_source.toml'))
        self.ammo = content_parser.load_content(os.path.join(path, 'content', 'items', 'ammo.toml'))
        for item in self.armor:
            self.equipment.append(item)
        for item in self.weapons:
            if item.type == 'melee':
                self.melee_weapons.append(item)
            if item.type == 'ranged':
                self.ranged_weapons.append(item)
            self.equipment.append(item)
        for item in self.monster_weapons:
            self.equipment.append(item)

    def sort_materials(self):
        """
        Sorts materials based on what it can be used to build
        :return:
        """
        for item in self.materials:
            if item.can_be_made_from == 1 or item.can_be_made_from == 3:
                self.weapon_mats.append(item)
            if item.can_be_made_from == 2 or item.can_be_made_from == 3:
                self.armor_mats.append(item)

    def sort_consumables(self):
        """
        Sorts potions and scrolls into separate containers
        :return:
        """
        for item in self.consumables:
            if item.type == 'potion':
                self.potions.append(item)
            if item.type == 'scroll':
                self.scrolls.append(item)

    def sort_equipment(self):
        """
        Sorts equipment based on type (eg. Melee, Ranged, Armor, Light Source, etc..)
        :return:
        """
        pass

    def sort_threat_levels(self):
        # TODO depreciate or expand upon
        lvl1 = []
        lvl2 = []
        lvl3 = []
        lvl4 = []
        for object in self.monsters:
            if object.threat_level <= 1.0:
                lvl1.append(object.name)
            if 1.0 < object.threat_level <= 2.0:
                lvl2.append(object.name)
            if 2.0 < object.threat_level <= 3.0:
                lvl3.append(object.name)
            if 3.0 < object.threat_level <= 4.0:
                lvl4.append(object.name)

        self.threat_list.append(lvl1)
        self.threat_list.append(lvl2)
        self.threat_list.append(lvl3)
        self.threat_list.append(lvl4)

    def get_random_monster_name(self):
        """
        Returns a parser class monster based on its name. Helper function to build a specific monster
        :return: The parser class Monster()
        """
        r = libtcod.random_get_int(0, 0, (len(self.monsters) - 1))
        return self.monsters[r].name

    def spell_component(self, type, name=None):
        """
        Builds a spell component for use by other constructors
        :param type: The type of spell component to return
        :param name: Optional: the name of the specific spell
        :return: Spell() class,  and the parser class of the specified type
        """
        sp = None
        if type == "potion":
            if name:
               sp = self.get_pot_from_name(name)
            if not name:  # in case you pass a name that doesnt exist, you get a random item
               sp = self.potions[libtcod.random_get_int(0, 0, (len(self.potions) - 1))]
        elif type == "scroll":
            if name:
                sp = self.get_scroll_from_name(name)
            if not name:
                sp = self.scrolls[libtcod.random_get_int(0, 0, (len(self.scrolls) - 1))]

        spell_component = spells.Spell()
        spell_component.min = sp.min_effect
        spell_component.max = sp.max_effect
        spell_component.range = sp.range
        spell_component.radius = sp.radius
        spell_component.type = sp.effect_type
        spell_component.effect_type = spells.spells[sp.effect_type]
        spell_component.addition_effects = sp.additional_effects
        spell_component.spell_effects = sp.spell_effect
        spell_component.effect_color = sp.effect_color

        return spell_component, sp

    def build_potion(self, game, x, y, name=None):
        """
        Builds a potion game object from required components
        :param game: the main game object
        :param x: x position on the map, can be 0 if going directly into inventory
        :param y: y position
        :param name: Optional, request a potion by the name (eg. "light healing")
        :return: the fully constructed object
        """

        spell_component, potion = self.spell_component('potion', name)
        item_component = Item()
        item_component.spell = spell_component
        item_component.use_function = item_component.spell.cast  # function pointer
        item_component.value = int(potion.value)
        item_component.stackable = True

        name = "potion of %s" % potion.name
        item = Object(game.dungeon_console, x, y, potion.cell, name, potion.color, item=item_component)
        item.char = chr(custom_font.big_potion)
        return item

    def build_scroll(self, game, x, y, name=None):
        """
        Builds a scroll game object from required components
        :param game: the main game object
        :param x: x position on the map, can be 0 if going directly into inventory
        :param y: y position
        :param name: Optional, request a potion by the name (eg. "light healing")
        :return: the fully constructed object
        """

        spell_component, scroll = self.spell_component('scroll', name)
        item_component = Item()
        item_component.spell = spell_component
        item_component.use_function = item_component.spell.cast  # function pointer
        item_component.value = int(scroll.value)
        item_component.stackable = True

        name = "scroll of %s" % scroll.name
        item = Object(game.dungeon_console, x, y, scroll.cell, name, scroll.color, item=item_component)
        item.char = chr(custom_font.scroll)
        return item

    def build_light_source(self, game, x, y, name=None):
        """
        Builds a light source game object from required components
        :param game: the main game object
        :param x: x position on the map, can be 0 if going directly into inventory
        :param y: y position
        :param name: Optional, request a potion by the name (eg. "light healing")
        :return: the fully constructed object
        """
        light = None
        if name:
            light = self.get_light_from_name(name)
        else:
            light = self.light_sources[libtcod.random_get_int(0, 0, len(self.light_sources)-1)]

        equip_component = Equipment()
        equip_component.type = light.type
        equip_component.fuel = light.max_fuel
        equip_component.max_fuel = light.max_fuel
        equip_component.torch_color = light.effect_color
        equip_component.torch_intensity = light.intensity

        item_component = Item()
        item_component.equipment = equip_component
        item_component.use_function = item_component.equipment.equip  # function pointer
        item_component.stackable = False
        item_component.value = int(light.value)

        equip = Object(game.dungeon_console, x, y, light.cell, light.name, light.color, item=item_component)
        equip.message = game.message
        equip.objects = game.objects

        return equip

    def build_equipment(self, game, x, y, type=None, name=None, mat=None):
        """
        todo: revist when subtypes are implemented
            # *note: subtypes are implemented*
        Builds a piece of equipment into a game usable object
        :param game: the main game object
        :param x: x position on the map, can be 0 if going directly into inventory
        :param y: y position
        :param type: Optional: Request a specific type of gear "armor, melee, etc.."
        :param name: Optional: Request a specific item by name "great sword"
        :param mat: Optional: request a specific mateiral to be used
        :return: a completed game Object.item.equipment()
        """
        equipment_types = ['melee', 'armor', 'ranged']  # random player equippable equipment, add extra types here
        random_equipment_types = {
            'melee': self.melee_weapons[libtcod.random_get_int(0, 0, (len(self.melee_weapons) - 1))],
            'ranged': self.ranged_weapons[libtcod.random_get_int(0, 0, len(self.ranged_weapons) - 1)],
            'monster_melee': self.monster_weapons[libtcod.random_get_int(0, 0, len(self.monster_weapons) - 1)],
            'armor': self.armor[libtcod.random_get_int(0, 0, (len(self.armor) - 1))],
        }

        if mat:
            mat = self.get_mat_from_name(mat)
        else:
            mat = self.materials[libtcod.random_get_int(0, 0, len(self.materials) - 1)]

        eq = None
        if type:
            eq = random_equipment_types[type]
        else:
            if name:
                eq = self.get_equip_from_name(name)
                if not eq:
                    eq = random_equipment_types[equipment_types[libtcod.random_get_int(0, 0, len(equipment_types) - 1)]]
            else:
                eq = random_equipment_types[equipment_types[libtcod.random_get_int(0, 0, len(equipment_types) - 1)]]

        equip_component = Equipment()
        equip_component.type = eq.type
        equip_component.mat = mat.name
        # equip_component.threat_level = eq.threat_level

        # todo revist after ranged weapons are in place
        if equip_component.type == 'melee' or equip_component.type == 'monster_melee' or equip_component.type == 'ranged':
            equip_component.handed = eq.handed
            equip_component.dual_wield = eq.dual_wield
            equip_component.accuracy = eq.accuracy
            equip_component.damage = eq.damage
            equip_component.damage_type = eq.damage_type
            equip_component.subtype = eq.subtype
        elif equip_component.type == 'armor':
            eq.bonus += mat.armor_bonus
            eq.penalty += mat.armor_bonus

            equip_component.location = eq.location
            equip_component.bonus = eq.bonus
            equip_component.penalty = eq.penalty

        if eq.type != "monster_melee":
            item_component = Item()
            item_component.equipment = equip_component
            item_component.use_function = item_component.equipment.equip
            item_component.value = int(eq.value * mat.price_mod)
            name = mat.name + " " + eq.name
            equip = Object(game.dungeon_console, x, y, eq.cell, name, mat.color, item=item_component)
        else:
            item_component = Item(equipment=equip_component)
            equip = Object(game.dungeon_console, x, y, ' ', eq.name, (0, 0, 0), item=item_component)
        equip.message = game.message
        equip.objects = game.objects

             ## TODO: REFACTOR - currently all items get an effect while testing
        effect = Effect(equip.item)                  # generate 2 effects randomly, linking them to the item
        effect_two = Effect(equip.item)
        equip.item.equipment.effects.append(effect)
        equip.item.equipment.effects.append(effect_two)

        char = self.get_custom_char(equip)
        if char:
            equip.char = char
        # equip.send_to_back(game.objects)
        return equip

    def build_ammo(self, game, x, y, weapon_type=None, name=None, mat=None):

        #### TODO MAKE IT NOT AS BORKED ####
        gear_panel = GearPanel(None)
        ammo_types = gear_panel.get_ammo_types()
        ####################################

        if mat:
            mat = self.get_mat_from_name(mat)
        else:
            mat = self.materials[libtcod.random_get_int(0, 0, len(self.materials) - 1)]

        ammo = None
        if weapon_type:
            ammo = self.get_ammo_from_weapon_type(ammo_types[weapon_type])
        else:
            if not name:
                name = ammo_types[libtcod.random_get_int(0, 0, len(ammo_types) - 1)]

            ammo = self.get_ammo_from_weapon_type(name)

        if not ammo:
            print("BORKD")
            return

        ammo_component = Ammo(weapon_type=ammo.weapon_type, max_stack=ammo.max_stack, dmg_multiplier=ammo.multiplier, col=ammo.col)

        item_component = Item(ammo=ammo_component)
        item_component.stackable = True
        item_component.qty = int(ammo.max_stack)
        item_component.value = int(ammo.value * mat.price_mod)
        name = mat.name + " " + ammo.name

        obj = Object(game.dungeon_console, x, y, ammo.cell, name, (255, 255, 255), item=item_component)

        return obj


    def create_monster(self, game, x, y, threat_level=None, mob_name=None):
        """
        Builds a fully created monster
        :param game:  The main game instance
        :param x: The x position of the monster
        :param y: The y position of hte monster
        :param threat_level: depreceated
        :param mob_name: Optional: spawn a specific monster
        :return: The ccompleted objects.fighter
        """
        if not mob_name:
            mob = self.monsters[libtcod.random_get_int(0, 0, len(self.monsters) - 1)]

        else:
            mob = self.get_monster(mob_name)
            if mob is None:  ##incase the name supplied is not in the monsters, get a random mob
                mob = self.monsters[libtcod.random_get_int(0, 0, len(self.monsters) - 1)]

        fighter_component = Fighter(0, 0, 0)  # todo remove calls from fighter() later?
        #fighter_component.max_hp = mob.hp                   # TODO REFACTOR
        #fighter_component.hp = mob.hp                       # TODO REFACTOR
        fighter_component.death_function = monster_death  # function pointer
        fighter_component.ticker = game.ticker
        #fighter_component.speed = mob.speed                 # TODO REFACTOR
        #fighter_component.stats[0] = mob.strength           # TODO REFACTOR
        #fighter_component.stats[1] = mob.dexterity          # TODO REFACTOR
        #fighter_component.stats[2] = mob.intelligence       # TODO REFACTOR
        #fighter_component.stats[3] = 10                     # TODO REFACTOR
        fighter_component.current_xp = mob.xp_value

        fighter_component.game = game

        ai_component = WanderingMonster(x=x, y=y)  # BasicMonster()

        monster = Object(game.dungeon_console, x, y, mob.cell, mob.name, mob.color,
                         blocks=True, fighter=fighter_component, ai=ai_component)
        monster.game = game
        #monster.fighter.ticker.schedule_turn(monster.fighter.speed, monster)  # TODO REFACTOR

        monster.fighter.stat.set_stat_base("HP", mob.hp)
        monster.fighter.hp = mob.hp             #TODO UNCOMMENT AFTER REFACTOR
        monster.fighter.stat.set_stat_base("Speed", mob.speed)
        monster.fighter.stat.set_stat_base("Strength", mob.strength)
        monster.fighter.stat.set_stat_base("Dexterity", mob.dexterity)
        monster.fighter.stat.set_stat_base("Intelligence", mob.intelligence)
        monster.fighter.stat.set_stat_base("Constitution",
                                           10)  # todo need this stat to be added to toml and file parser

        monster.fighter.ticker.schedule_turn(monster.fighter.stat.get_stat("Speed"), monster) #TODO UNCOMMENT AFTER REFACTOR

        # todo fix when either AI director is ready to spawn mobs, or when effects system is enabled
        # this is why effects aren't working, we have to equip it using gear panel for it to activate properly
        # monster.fighter.gear.equipped['1h'] = self.build_equipment(game, x, y, type="monster_melee")
        if mob.can_equip_gear:
            r = libtcod.random_get_int(0, 0, 100)
            if r > 85:  # 15 % chance the mob will have a weapon (unless it spawns a shield
                gear = self.build_equipment(game, x, y, type="melee")
                if gear.item.equipment.subtype != "Shield":
                    monster.fighter.gear.quip_it(gear)
            # for slots in monster.fighter.gear.armor_panel:
            #   if libtcod.random_get_int(0, 0, 100) < 10:   # 10% chance of gear on each slot
        if monster.fighter.gear.equipped['1h'] is None:
            monster.fighter.gear.quip_it(self.build_equipment(game, x, y, type="monster_melee"))

        for skill in monster.fighter.skills:
            skill.set_bonus(mob.defense_bonus)

        return monster

    def get_monster(self, name):
        """
        Returns a parser monster class by name
        :param name:  Name of the monster to grab
        :return: parser.Monster() class or None
        """
        for object in self.monsters:
            if object.name == name:
                return object
        return None

    def get_threat_from_mob(self, mob_name):
        # todo probably remove
        ##returns the threat level of a mob based on its name
        for obj in self.monsters:
            # logging.getLogger('main').debug(obj.threat_level)
            if obj.name == mob_name:
                return obj.threat_level
        return False

    def get_mob_from_threat(self, threat_level=None):  ##basic setup
        # todo probably remove
        if threat_level is None:
            if libtcod.random_get_int(0, 0, 100) < 80:  # 80% chance of threat level less than 4
                if libtcod.random_get_int(0, 0, 100) < 30:  # 30% chance of getting lvl 3
                    tl = self.threat_list[2]
                    return tl[libtcod.random_get_int(0, 0, (len(tl) - 1))]
                if libtcod.random_get_int(0, 0, 100) < 50:  # 50% chance of getting lvl 2
                    tl = self.threat_list[1]
                    return tl[libtcod.random_get_int(0, 0, (len(tl) - 1))]
                if libtcod.random_get_int(0, 0, 100) < 80:  # 80% chance of getting lvl 1
                    tl = self.threat_list[0]
                    return tl[libtcod.random_get_int(0, 0, (len(tl) - 1))]
            else:
                tl = self.threat_list[3]
                return tl[libtcod.random_get_int(0, 0, (len(tl) - 1))]
        else:
            if threat_level - 1 >= len(self.threat_list):
                threat_level = len(self.threat_list)
            if threat_level - 1 < 0:
                threat_level = 0
            tl = self.threat_list[threat_level - 1]
            return tl[libtcod.random_get_int(0, 0, (len(tl) - 1))]

    def get_light_from_name(self, name):
        """
        Returns a parser light source class by name
        :param name:  Name of the light source to grab
        :return: parser.LightSource() class or None
        """
        for light in self.light_sources:
            if light.name == name:
                return light
        return None

    def get_pot_from_name(self, name):
        """
        Returns a parser potion class by name
        :param name:  Name of the potion to grab
        :return: parser.Potion() class or None
        """
        for pot in self.potions:
            if pot.name == name:
                return pot
        return None

    def get_scroll_from_name(self, name):
        """
        Returns a parser scroll class by name
        :param name:  Name of the scroll to grab
        :return: parser.Scroll() class or None
        """
        for scroll in self.scrolls:
            if scroll.name == name:
                return scroll
        return None

    def get_mat_from_name(self, name):
        """
        Returns a parser material class by name
        :param name:  Name of the material to grab
        :return: parser.Material() class or None
        """
        for mat in self.armor_mats:
            if mat.name == name:
                return mat
        for mat in self.weapon_mats:
            if mat.name == name:
                return mat
        return None

    def get_mat_from_rarity(self, type):
        # todo enable rarity or remove
        r = libtcod.random_get_float(0, 0.00000, 1.00000)
        mat = None
        rarity = 1.0
        if type == 'melee':
            for mats in self.weapon_mats:
                if mats.rarity >= r:
                    if mats.rarity <= rarity:
                        rarity = mats.rarity
                        mat = mats
            return mat
        if type == 'armor':
            for mats in self.armor_mats:
                if mats.rarity >= r:
                    if mats.rarity <= rarity:
                        rarity = mats.rarity
                        mat = mats
            return mat
        return self.materials[0]

    def get_equip_from_name(self, name):
        """
        Returns a parser equipment type by name
        :param name:  Name of the equipment to grab
        :return: Melee, Ranged, MonsterWeapon, Armor, etc.. class or None
        """
        for equip in self.equipment:
            if equip.name == name:
                return equip
        return None

    def get_ammo_from_weapon_type(self, name):
        for ammo in self.ammo:
            if ammo.weapon_type == name:
                return ammo
        return None

    def get_custom_char(self, obj):
        if hasattr(obj, "item"):
            if hasattr(obj.item, "spell") and obj.item.spell:
                return chr(custom_font.scroll)
            elif hasattr(obj.item, "equipment") and obj.item.equipment:
                if obj.item.equipment.subtype:  # its a weapon
                    if obj.item.equipment.subtype == "Shield":
                        return chr(custom_font.shield)
                    if obj.item.equipment.subtype == "Long Sword":
                        return chr(custom_font.long_sword)
                    if obj.item.equipment.subtype == "Dagger":
                        return chr(custom_font.dagger)
                    if obj.item.equipment.subtype == "Short Sword":
                        return chr(custom_font.short_sword)
                    if obj.item.equipment.subtype == "Great Sword":
                        return chr(custom_font.great_sword)
                    if obj.item.equipment.subtype == "Mace":
                        return chr(custom_font.mace)
                    if obj.item.equipment.subtype == "Hammer":
                        return chr(custom_font.hammer)
                    if obj.item.equipment.subtype == "Great Hammer":
                        return chr(custom_font.two_handed_hammer)
                    if obj.item.equipment.subtype == "Hand Axe":
                        return chr(custom_font.hand_axe)
                    if obj.item.equipment.subtype == "Battle Axe":
                        return chr(custom_font.battle_axe)
                else:  # its an armor
                    if obj.item.equipment.location == "Head":
                        return chr(custom_font.helm)
                    if obj.item.equipment.location == "Hands":
                        return chr(custom_font.glove)
                    if obj.item.equipment.location == "Shoulders":
                        return chr(custom_font.shoulder)
                    if obj.item.equipment.location == "Arms":
                        return chr(custom_font.arms)
                    if obj.item.equipment.location == "Torso":
                        return chr(custom_font.torso)
                    if obj.item.equipment.location == "Legs":
                        return chr(custom_font.legs)
                    if obj.item.equipment.location == "Feet":
                        return chr(custom_font.boot)
                    if obj.item.equipment.location == "Cloak":
                        return chr(custom_font.cloak)
                    if obj.item.equipment.location == "Neck":
                        return chr(custom_font.neck)
                    if obj.item.equipment.location == "Ring":
                        return chr(custom_font.ring)
            elif hasattr(obj.item, "ammo") and obj.item.ammo:
                pass
            else:  # its a regular ass bitch ass item
                pass