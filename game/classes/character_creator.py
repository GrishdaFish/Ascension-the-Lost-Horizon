__author__ = 'GrishdaFish'

from gEngine.utilities.widget import window_widget, button_widget, text_input_widget, button_group, popups

from game.debug_modules import module_list, dungeon_status, spawning_tool, reload_module

from game.user_interface import help_popup_module

from game import game

from game.spells import spells

from game.classes import skills
from game.classes import warrior_skills

from game.object import effects

import tcod as libtcod

import textwrap
import random

class CharacterCreator(window_widget.WindowWidget):
    def setup(self):
        self.g = game.Game(self.gEngine)
        self.base_width = 25
        self.max_width = 38
        self.buttons = []
        self.perk_packages = []
        self.selected_perk = None

        create_perk_package(1, 10, self)
        create_perk_package(20, 10, self)
        create_perk_package(1, 20, self)
        create_perk_package(20, 20, self)

        self.warrior_description = True
        self.wizard_description = False
        self.paladin_description = False
        self.ranger_description = False
        self.rogue_description = False

        self.display_description = False

        self.c_name = text_input_widget.TextInputWidget(self, 1, 1, "Name: ", self.max_width)
        self.c_name.default_text = "Player Name"
        self.buttons.append(self.c_name)
        self.exit_button = button_widget.ButtonWidget(self, 1, self.gEngine.h-2, "Finish", self.finish)
        self.buttons.append(self.exit_button)

        self.m_tutorial_group = button_group.ButtonGroupWidget(self, 11, 6, 4, 1)
        self.tutorial_on_button = button_group.GroupButton(self.m_tutorial_group, 1, 0, "Yes")
        self.m_tutorial_group.add_button(self.tutorial_on_button)

        self.c_class_group = button_group.ButtonGroupWidget(self, 1, 4, self.max_width)
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Warrior", self.activate_warrior))
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Wizard", self.activate_wizard))

        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Ranger"))

        self.g.new_game()

        frames = ['wall_torch_a', 'wall_torch_b', 'wall_torch_c', 'wall_torch_d']
        self.gEngine.animation_add_cell_animation(self.con, frames, True, 2, 2, delay=5, fore=False)
        frames = ['wall_torch_a', 'wall_torch_b', 'wall_torch_c', 'wall_torch_d']
        self.gEngine.animation_add_cell_animation(self.con, frames, True, 3, 2, delay=5, fore=True)



    def update(self, key, mouse):
        #self.gEngine.console_clear(self.con)
        self.gEngine.console_vline(self.con, self.max_width + 2, 1, self.height - 2)
        self.gEngine.console_print(self.con, 1, 3, "Select your class: ")
        self.gEngine.console_print(self.con, 1, 6, "Tutorial? ")
        self.gEngine.console_print(self.con, 1, 8, "Select one of the perk packages below ")

        self.gEngine.console_hline(self.con, self.width / 2, self.height / 2, self.width / 2)
        self.gEngine.console_print(self.con, self.width / 2, self.height / 2, chr(libtcod.CHAR_TEEE))

        self.gEngine.console_print(self.con, self.width - 1, self.height / 2, chr(libtcod.CHAR_TEEW))

        for button in self.buttons:
            button.run(key, mouse)

        self.gEngine.animation_draw_animations_back(False)
        self.gEngine.animation_draw_animations_fore(False)
        self.c_class_group.run(key, mouse)
        self.m_tutorial_group.run(key, mouse)
        self.description()

    def close(self):
        pass

    def finish(self):

        self.gEngine.modules = []
        self.gEngine.additional_modules = []
        self.gEngine.module_adjust_list = []

        self.create_player()
        self.gEngine.add_module(self.g)

        d = dungeon_status.DungeonStatus(self.gEngine, self.g, 5, 6, self.gEngine.SCREEN_WIDTH / 2, 7, "Dungeon Status")
        d.deactivate()
        self.gEngine.add_module(d)

        spawn_tool = spawning_tool.SpawningTools(self.gEngine, self.g, 0, 0, 18, 9, "Spawning Tools")
        spawn_tool.setup()
        self.gEngine.add_module(spawn_tool)

        # load this module last
        m = module_list.ModuleList(self.gEngine, self.g, 0, 0, 15, 5, 'Module List')
        self.gEngine.add_module(m)

        r = reload_module.ReloadModule(self.gEngine, x=20, y=0, w=15,h=5,title="Reload Tool")
        r.setup()
        r.activate()
        self.gEngine.add_module(r)

        help_module = help_popup_module.HelpPopup(self.gEngine, self.g, 5, 5, 70, 30, "Help")
        if self.tutorial_on_button.enabled:
            help_module.activate()
        else:
            help_module.deactivate()
        self.gEngine.add_module(help_module)

    def activate_warrior(self):
        self.warrior_description = True
        self.wizard_description = False
        self.display_description = True
        self.create_warrior()

    def activate_wizard(self):
        self.wizard_description = True
        self.warrior_description = False

        self.display_description = True

    def description(self):
        text = ""
        if self.warrior_description:
            text = "Melee based class focusing on offense and 2 handed weapons with wide sweeping attacks. " \
                   "High health but low magical ability. Limited scroll usage, but increased torch and lantern duration. " \
                   "Uses heavy armor with less penalties, light armor with no penalties and no armor with bonuses. "
        if self.wizard_description:
            text = "Magic based class that uses torch and lantern power to fuel magical attacks. Can use all wands and " \
                   "scrolls. Can learn spells from scrolls, and permanently cast using lantern power. Unable to use " \
                   "armor, and melee weapons other than staves. Staves are weak single target only weapons."
        if self.paladin_description:
            text = "Paladins are divine warriors that use favor from their chosen god to empower their attacks, smite " \
                   "and blind their foes with divine light."
        if self.ranger_description:
            text = "Rangers are a ranged class focusing on bows and crossbows to keep their foes at range. They have " \
                   "limited access to scrolls but can create makeshift torches out of objects they find in the dungeon."
        if self.rogue_description:
            text = "Rogues are stealthy melee class that focuses on attacking unaware monsters. Masters of shadow, they " \
                   "prefer darkness and have better low light vision than other classes. Has an affinity for wands and " \
                   "other magical objects."
        if self.display_description:
            self.wrapped_text = textwrap.wrap(text, self.max_width)
            l = 0
            for line in self.wrapped_text:
                l += 1
                self.gEngine.console_print(self.con, self.max_width+3, l, line)
        text = ""
        inv = "Inventory Items: "
        for item in self.g.player.fighter.inventory:
            t = self.gEngine.color_text(item.name, item.color)
            t += t + " (%d)"%item.item.qty
            inv += "%s, "%t
        p = self.g.player.fighter
        self.gEngine.console_print(self.con, self.width / 2 +1, self.height / 2 +1, 'STR DEX CON INT')
        self.gEngine.console_print(self.con, self.width / 2 + 1, self.height / 2 + 2, '%d  %d  %d  %d'
                                   % (p.stat.get_stat('Strength'),
                                      p.stat.get_stat('Dexterity'),
                                      p.stat.get_stat('Constitution'),
                                      p.stat.get_stat('Intelligence')))
        text += inv
        l = self.height/2 + 3
        wrapped = textwrap.wrap(text, self.width/2 - 2)
        for line in wrapped:
            self.gEngine.console_print(self.con, self.width /2 + 1, l, line)
            l += 1

    def create_player(self):
        self.g.player.name = self.c_name.text_field

        if self.warrior_description:
            self.create_warrior()
        if self.wizard_description:
            self.create_wizard()
        if self.paladin_description:
            self.create_paladin()
        if self.ranger_description:
            self.create_ranger()
        if self.rogue_description:
            self.create_rogue()

    def create_warrior(self): # TODO: Break this out into its own .py file
        inv = self.g.player.fighter.inventory
        # inv = []
        print(self.g.player.name)
        weapon = self.g.build_objects.build_equipment(self.g, 0, 0, name="Great Sword", mat="Iron")
        # weapon.item.equipment.on_hit_effect = spells.explosion # Testing on hit effects

        weapon.item.pick_up(inv)
        chest = self.g.build_objects.build_equipment(self.g, 0, 0, name="plate", mat="Iron")
        chest.item.pick_up(inv)
        head = self.g.build_objects.build_equipment(self.g, 0, 0, name="plate helm", mat="Iron")
        head.item.pick_up(inv)
        for i in range(2):
            t = self.g.build_objects.build_light_source(self.g, 0, 0, "torch")
            t.item.pick_up(inv)
        for x in range(5):
            p = self.g.build_objects.build_potion(self.g, 0, 0, 'healing')
            p.item.pick_up(inv)
        for x in range(20):
            s = self.g.build_objects.build_scroll(self.g, 0, 0, 'fireball')
            s.item.pick_up(inv)

        #Stats
        if self.selected_perk:
            self.g.player.fighter.stat.set_stat_base("Strength", self.selected_perk.strength)
            self.g.player.fighter.stat.set_stat_base("Dexterity", self.selected_perk.dexterity)
            self.g.player.fighter.stat.set_stat_base("Constitution", self.selected_perk.constitution)
            self.g.player.fighter.stat.set_stat_base("Intelligence", self.selected_perk.intelligence)
        self.g.player.fighter.stat.set_stat_base("HP", 75)
        self.g.player.fighter.stat.set_stat_base("Stamina", 10)

        self.g.player.fighter.stamina = 1
        self.g.player.fighter.hp = 75
        self.g.player.fighter.max_consumable_level = 3
        self.g.player.fighter.money = 200

        #Passive Skills
        self.g.player.fighter.passives = []
        weapon_subtype = "Great Sword"
        self.g.player.fighter.weapon_profs.update({weapon_subtype:self.g.weapon_prof_skills[weapon_subtype]})
        self.g.player.fighter.passives.append(self.g.weapon_prof_skills[weapon_subtype])
        # self.g.passive_skills.remove(self.g.weapon_prof_skills[weapon_subtype])

        weapon_subtype = "Long Sword"
        self.g.player.fighter.weapon_profs.update({weapon_subtype: self.g.weapon_prof_skills[weapon_subtype]})
        self.g.player.fighter.passives.append(self.g.weapon_prof_skills[weapon_subtype])
        # self.g.passive_skills.remove(self.g.weapon_prof_skills[weapon_subtype])

        #Active Cooldown Skills
        self.g.player.fighter.active_skills = []
        ww = skills.CooldownSkill("Whirlwind", self.g.player, "Whirlwind skill", 3, warrior_skills.whirlwind, self.g, self.gEngine,"W")
        self.g.player.fighter.active_skills.append(ww)

        #Active Spender Skills
        b = skills.ResourceSkill("Bash", self.g.player,"Bash Skill", 3, warrior_skills.bash, self.g, self.gEngine,"B")
        self.g.active_skills.append(b)
        #self.g.player.fighter.active_skills.append(b)


    def create_wizard(self):
        pass

    def create_paladin(self):
        pass

    def create_ranger(self):
        pass

    def create_rogue(self):
        pass

    def generate_perk_packages(self):
        # warrior package
        pass

        # wizard package
        pass

        # Ranger package
        pass

        # rogue package
        pass

    def select_package(self, perk, button):
        self.selected_perk = perk
        if self.selected_perk:
            self.g.player.fighter.stat.set_stat_base("Strength", self.selected_perk.strength)
            self.g.player.fighter.stat.set_stat_base("Dexterity", self.selected_perk.dexterity)
            self.g.player.fighter.stat.set_stat_base("Constitution", self.selected_perk.constitution)
            self.g.player.fighter.stat.set_stat_base("Intelligence", self.selected_perk.intelligence)
        button.background_color = libtcod.grey
        for b in self.buttons:
            if isinstance(b, button_widget.BigButtonWidget):
                if b == button:
                    pass
                else:
                    b.background_color = libtcod.black


def create_perk_package(x=0, y=0, owner=None):
    p = PerkPackage()
    l = [
        'Perk Package',
        'STR DEX CON INT',
        '%d  %d  %d  %d' % (p.strength, p.dexterity, p.constitution, p.intelligence),
        '%s' % p.perk_bonus1.name,
        '%s' % p.perk_bonus2.name,
        '%s' % p.perk_bonus3.name,
        '%s' % p.perk_bonus4.name
    ]
    test_perk_package = button_widget.BigButtonWidget(owner, x, y, label=l, function=owner.select_package, passable=[p])
    test_perk_package.passable.append(test_perk_package)
    test_perk_package.background_color = libtcod.black
    owner.buttons.append(test_perk_package)
    owner.perk_packages.append(p)
    #return p, l

class PerkPackage:
    def __init__(self):
        self.perk_bonus1 = self.roll_perk()
        self.perk_bonus2 = self.roll_perk()
        self.perk_bonus3 = self.roll_perk()
        self.perk_bonus4 = self.roll_perk()

        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        self.constitution = 10

        self.roll_stats()

    def roll_stats(self):
        stat_total = 54
        rolls = []
        for x in range(3):
            roll = libtcod.random_get_int(0, 9, 18)
            rolls.append(roll)
            stat_total -= roll
        if stat_total > 20:
            rollover = stat_total - 20
            stat_total -= rollover
            rollover = int(rollover - len(rolls))
            for roll in rolls:
                roll += rollover
        rolls.append(stat_total)
        r = libtcod.random_get_int(0, 10, 100)
        for x in range(r):
            random.shuffle(rolls)
        self.strength = rolls[0]
        self.dexterity = rolls[1]
        self.intelligence = rolls[2]
        self.constitution = rolls[3]

    def roll_perk(self):
        s = libtcod.random_get_int(0, 1, 100)
        return skills.ResourceSkill("TestSkill%s"%int(s))