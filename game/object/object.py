import sys
import os
import math
import copy
import logging

from game.object.gear_panel import GearPanel
from game.object.item import Equipment, Item
from game.object.stat_panel import StatPanel

sys.path.append(sys.path[0])
import tcod as libtcod
from game import combat, combat_controller
from game import bark
from gEngine import lights

# I might rewrite this system, the bigger the game gets, the more cumbersome this
# system gets. :(
class Object:
    '''this is a generic object: the player, a monster, an item, the stairs...
    it's always represented by a character on screen.'''

    def __init__(self, con=None, x=None, y=None, char=None, name=None, color=None,
                 blocks=False, fighter=None, ai=None, item=None, misc=None, projectile=None,
                 npc=None, torch=None):

        self.con = con
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.base_color = color
        self.flash_color = None
        self.blocks = blocks
        self.objects = None
        self.message = None
        self.type = None
        self.flashing = False
        self.flash_duration = 0

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self
            self.ai.node = None

        self.item = item
        if self.item:
            self.item.owner = self

        self.misc = misc
        if self.misc:
            self.misc.owner = self

        self.projectile = projectile
        if self.projectile:
            self.projectile.owner = self

        self.npc = npc
        if self.npc:
            self.npc.owner = self

        self.torch = torch
        if self.torch:
            self.torch.owner = self

    def move(self, dx, dy, map, objects):
        # move by the given amount, if the destination is not blocked
        if not self.is_blocked(self.x + dx, self.y + dy, map, objects):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y, map, objects):
        # vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy, map, objects)

    def distance_to(self, other):
        # return the distance to another object
        if other:
            dx = other.x - self.x
            dy = other.y - self.y
            v = (dx ** 2) + (dy ** 2)
            return math.sqrt(int(v))

    def distance(self, x, y):
        # return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self, objects=None):
        # make this object be drawn first, so all others appear above it if they're in the same tile.
        if objects is None:
            self.objects.remove(self)
            self.objects.insert(0, self)
        else:
            objects.remove(self)
            objects.insert(0, self)

    def attack_torch(self, torch):
        self.torch = torch
        self.torch.owner = self

    def draw(self, fov_map, gEngine, is_player=False, force_display=False):
        # only show if it's visible to the player
        if force_display:
            # print gEngine.return_color_background(self.con,self.x,self.y)
            col = gEngine.get_map_tile_color(int(self.x), int(self.y))
            brightness = gEngine.lightmask_get_mask_value(self.x, self.y)
            fr, fg, fb = self.color
            br, bg, bb = col
            br *= brightness[0]
            bg *= brightness[1]
            bb *= brightness[2]
            br = min(255, br)
            bg = min(255, bg)
            bb = min(255, bb)
            gEngine.console_put_char_ex(self.con, int(self.x), int(self.y), self.char, fr, fg, fb,
                                        int(br), int(bg), int(bb))  # self.char,self.color,col)

        elif gEngine.map_is_in_fov(int(self.x), int(self.y)):
            # set the color and then draw the character that represents this object at its position
            # h, s, v = gEngine.console_get_char_background(self.con, int(self.x), int(self.y))
            # col = libtcod.Color(int(h), int(s), int(v))
            # libtcod.color_set_hsv(col, h, s, v)
            col = gEngine.get_map_tile_color(int(self.x), int(self.y))
            br, bg, bb = col
            fr, fg, fb = 0, 0, 0
            if self.flashing:
                if self.flash_duration == 1:
                    c2 = libtcod.Color(0, 0, 0)
                    libtcod.color_set_hsv(c2, 0, 0, 255)
                    fr, rg, rb = c2
                    self.flash_duration = 0
                    self.flashing = False
            else:  # TODO CONSIDER calculate final colors in a separate function? This may be the only spot to do this
                fr, fg, fb = self.color
                brightness = gEngine.lightmask_get_mask_value(self.x, self.y)
                fr *= brightness[0]
                fg *= brightness[1]
                fb *= brightness[2]
                br *= brightness[0]
                bg *= brightness[1]
                bb *= brightness[2]
            fr = min(255, fr)
            fg = min(255, fg)
            fb = min(255, fb)
            br = min(255, br)
            bg = min(255, bg)
            bb = min(255, bb)

            if is_player:  # TODO NOTE This  will be needed if we do a scrolling map
                gEngine.console_put_char_ex(self.con, gEngine.w / 2, gEngine.h / 2 - 6, self.char, int(fr), int(fg),
                                            int(fb), int(br), int(bg), int(bb))
            else:
                gEngine.console_put_char_ex(self.con, int(self.x), int(self.y), self.char, int(fr), int(fg), int(fb),
                                            int(br), int(bg), int(bb))  # self.char,self.color,col)

    def clear(self, gEngine):
        # erase the character that represents this object
        gEngine.console_set_char(self.con, self.x, self.y, " ")

    def is_blocked(self, x, y, map, objects):
        # first test the map tile
        if map[int(x)][int(y)].blocked:
            return True

        # now check for any blocking objects
        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        return False

    def short_flash(self):
        pass

    def long_flash(self):
        pass

    def blink(self):
        pass

    def hover_description(self):
        names = []
        if self.fighter is not None:
            names = [self.name, "HP: " + str(self.fighter.hp) + "/" + str(self.fighter.stat.get_stat("HP")), "Gear: "]
            for each_gear in self.fighter.gear.gimmie_da_quips():
                if each_gear is not None:
                    names.append(each_gear.item.owner.name)
                    if len(each_gear.item.equipment.effects) > 0:
                        for each_effect in each_gear.item.equipment.effects:
                            line = "%s: %d %s" % (each_effect.effect_name, each_effect.amount, each_effect.effect_real_name)
                            names.append(line)

        if self.item is not None:
            names = [self.name, "Value: " + str(self.item.value)]
            if self.item.equipment is not None:
                if self.item.equipment is not None:
                    names.append(self.item.equipment.description)
                    if self.item.equipment.defense == 0:
                        names.append("Defense: " + str(self.item.equipment.defense))
                    if self.item.equipment.damage is not None:
                        names.append("Damage: " + str(self.item.equipment.damage))
                    if len(self.item.equipment.effects) > 0:
                        for each_effect in self.item.equipment.effects:
                            line = "%s: %d %s" % (each_effect.effect_name, each_effect.amount, each_effect.effect_real_name)
                            names.append(line)
            if self.item.spell is not None:
                names.append(self.item.spell.type)
        return names

class Fighter:
    # combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None, Con=10, Str=10, Dex=10, Int=10, money=0, ticker=None,
                 speed=0, xp_value=0):

        self.stat = StatPanel()      # damage, resistance, effects and conditions
        self.gear = GearPanel(self)  # equipped items and related controls
        # Achievement tracker will go here if implemented

        self.death_function = death_function
        self.type = 'melee'
        self.money = money
        # self.speed = speed  # TODO REFACTOR this is in skill panel now
        self.level = 1
        self.current_xp = xp_value
        self.xp_to_next_level = 1  # if you don't set this to something before you use log, you gonna die.
        self.xp_to_next_level = self.get_xp_tnl()
        self.inventory = []
        self.owner = None
        self.ticker = ticker
        # self.stats = [Str, Dex, Int, Con]   # TODO REFACTOR this is in skill panel now
        self.unused_skill_points = 2
        # self.defense = 0    # TODO REFACTOR in skill panel, not implemented

        self.depth = 0
        self.threat = 0.0

        self.max_hp = self.stat.get_stat("HP")  # REFACTOR get hp from stats now
        self.hp = self.max_hp
        # self.hp = hp

        # self.armor_bonus = 0  is now "Defense modifier" in stat panel
        # self.armor_penalty = 0 is now "Evasion penalty" in stat panel

        self.skills = copy.deepcopy(combat.skill_list)  # skill list needs to have its own copies

        '''self.max_mp = 1 + (2*self.stats[2])
        mp = self.max_mp
        self.mp = mp'''
        ################################################################################################################
        # TODO
        #      .UPDATE. this should all be done now If no relics found in play test
        #               then all this can safely be deleted
        # logically linked to self.gear.equipped
        #self.equipment = [ self.gear.equipped['Head'],
        #                   self.gear.equipped['Shoulders'],
        #                   self.gear.equipped['Arms'],
        #                   self.gear.equipped['Hands'],
        #                   self.gear.equipped['Torso'],
        #                   self.gear.equipped['Legs'],
        #                   self.gear.equipped['Feet'],
        #                   self.gear.equipped['Cloak']
        #                    ]
        # logically linked to self.gear.light_source
        #self.light_source = self.gear.light_source
        # logically linked to self.gear.equipped
        #self.accessories = [self.gear.equipped['Neck'],
        #                    self.gear.equipped['Ring']
        #                    ]
        # logically linked to self.gear.equipped
        #self.wielded = [self.gear.equipped['1h'], self.gear.equipped['2h']]
        ################################################################################################################

    def get_xp_tnl(self):       # TODO TESTING make sure values are stable and realistic
        lv_basis = self.level*2    # ARBITRARY BASIS FOR SCALING
        log_base = 10              # JUST GO WITH BASE 10 FOR NOW
        modifier = 10000           # MODIFIER TAKES YOU FROM SINGLE DIGITS UP INTO REALISTIC VALUES
        added_xp = math.log(lv_basis, log_base)
        added_xp *= modifier
        xp_to_next_level = (self.xp_to_next_level + int(added_xp))
        return xp_to_next_level

    def get_lv_up_sp(self):     # TODO TESTING make sure values are stable in range 1 : 5
        sp = int(self.level / 2)
        sp_add = 1 if sp < 1 else sp
        sp_add = 5 if sp > 5 else sp
        return sp_add

    def level_up(self):         # TODO DEVELOP make additional stat stuff happen - level up magic
        self.level += 1
        self.current_xp -= self.xp_to_next_level
        self.xp_to_next_level = self.get_xp_tnl()
        # TODO skill points aren't actually doing anything currently
        sp = self.get_lv_up_sp()
        self.unused_skill_points += sp

        add_hp = 2                                              # you get 2 hp at least no matter what
        add_hp += int(self.stat.get_stat("Constitution") / 4)   # 25% of con as bonus seems low @start/high for end game
        add_hp += self.stat.get_stat_base("HP")                 # add bonus to current
        self.stat.set_stat_base("HP", add_hp)                   # set it in stat_panel
        self.hp = self.stat.get_stat("HP")                      # replenish hp to max

        # these will all be decided by build type.
        # For now im just giving each a random 0-2 point boost each level for shits
        self.stat.set_stat_base("Strength", (self.stat.get_stat_base("Strength") + libtcod.random_get_int(0, 0, 2)))
        self.stat.set_stat_base("Dexterity", (self.stat.get_stat_base("Dexterity") + libtcod.random_get_int(0, 0, 2)))
        self.stat.set_stat_base("Constitution", (self.stat.get_stat_base("Constitution") + libtcod.random_get_int(0, 0, 2)))
        self.stat.set_stat_base("Intelligence", (self.stat.get_stat_base("Intelligence") + libtcod.random_get_int(0, 0, 2)))


    def apply_skill_points(self, skill):
        if isinstance(skill, str):
            skill = self.get_skill(skill)
        self.unused_skill_points = skill.increase_level(self.unused_skill_points)

    """
    def set_armor_bonus(self):
        bonus = 0
        for item in self.equipment:
            if item is not None:
                bonus += item.item.equipment.bonus
        self.armor_bonus = bonus

    def get_armor_bonus(self):
        return self.armor_bonus

    def get_armor_penalty(self):
        return self.armor_penalty

    def set_armor_penalty(self):
        penalty = 0
        for item in self.equipment:
            if item is not None:
                penalty += item.item.equipment.penalty
        penalty -= self.get_skill('Armor').get_bonus()
        self.armor_penalty = penalty
    """
    def get_skill(self, name):
        for skill in self.skills:
            if skill.get_name() == name:
                return skill
        return None

    def ranged_targeted_attack(self, target, player=False, game=None):
        # wehen you click a mob with a ranged weapon equipped it should pop up a menu to select from available projectiles for current weapon
        if not player:
            col = 2
        else:
            col = 5
        msg = "shot " + target.name + "! PEW PEW"
        if game:
            game.message.message(msg, col)

    def attack(self, target, player=False, direction=None, game=None, force_attack=False):
        print("Attacking")
        if force_attack:
            combat_controller.attack(self, direction=None, force_attack_target=target)
        else:
            combat_controller.attack(self, direction)

        """if not player:
            col = 2
        else:
            col = 5

        attack_roll = libtcod.random_get_int(0, 1, 20)
        attack_roll += combat.get_melee_bonus(self.owner)

        evasion_roll = combat.get_evasion_class(target)
        deflection_roll = combat.get_deflection_class(target)
        blocking_roll = combat.get_blocking_class(target)

        # msg = "A: %d, E:%d" % (attack_roll, evasion_roll)
        # self.owner.message.message(msg)
        msg = ''
        if evasion_roll > attack_roll:
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was evaded!'
        elif deflection_roll > attack_roll:  # need to check for a weapon or something that can deflect
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was deflected!'
        elif blocking_roll > attack_roll:  # need to check for shield
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was blocked!'
        else:
            dmg = 0
            if self.gear.equipped['1h'] is not None:
                skill = self.get_skill(self.gear.equipped['1h'].item.equipment.damage_type)
                if skill is not None:
                    dmg = skill.get_bonus()
                if dmg is None:
                    dmg = 0
                dmg += self.gear.equipped['1h'].item.equipment.calc_damage()
                if self == game.player.fighter: # TODO this should apply to mobs, but for now just player because monster melee doesnt level
                    self.gear.add_w_xp(self.gear.equipped['1h'].item.equipment.subtype, 100)  # TODO 100 xp per strike for now
                # TODO if duals get that damage calc too, quick and dirty below:
                dmg2 = None
                if self.gear.equipped['2h'] is not None:
                    skill = self.get_skill(self.gear.equipped['2h'].item.equipment.damage_type)
                    if skill is not None:
                        dmg2 = skill.get_bonus()
                    if dmg2 is None:
                        dmg2 = 0
                    dmg2 += self.gear.equipped['2h'].item.equipment.calc_damage()
                    if self == game.player.fighter:  # TODO this should apply to mobs, but for now just player
                        self.gear.add_w_xp(self.gear.get_quipped_weapon_type(off_hand=True), 100)
                # TODO also, shield defense, the above makes shiedls do damage, WOOT !
                if dmg2: # if dealing 2h damage
                    dmg = int(dmg + dmg2)
                else:
                    dmg = int(dmg)
            else:
                # For empty slots
                pass
            if dmg > 0:
                if attack_roll < 10 + self.gear.get_stat("Defense"):  # armor_bonus:
                    dmg *= 0.25
                    dmg = int(dmg)
                # TODO CONSIDER this is where conditions are applied currently
                if self.stat.conditions:
                    for fx in self.stat.conditions:
                        fx.inflict_condition(target.fighter)
                # make the target take some damage
                target.fighter.take_damage(dmg, self.owner, game)
                msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(dmg) + '!'
            else:
                if libtcod.random_get_int(0, 0, 100) < 25:  # 25% chance to always do at least 1 damage
                    dmg = 1
                    target.fighter.take_damage(dmg, self.owner, game)
                    msg = self.owner.name.capitalize() + ' scratches ' + target.name + ' for ' + str(dmg) + '!'
                else:
                    msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'
        if game:
            game.message.message(msg, col)
            # TODO REFACTOR isolate and build
        # expand on this for different attack patterns, right now its a 1x3 area in front of the player
        if direction and player:
            t = None
            if direction == "north" or direction == 'south':
                t = game.check_for_target(target.x + 1, target.y)
                if t:
                    game.player.fighter.attack(t, player=True, game=game)
                    t = None
                t = game.check_for_target(target.x - 1, target.y)
                if t:
                    game.player.fighter.attack(t, player=True, game=game)
            elif direction == "east" or direction == 'west':
                t = game.check_for_target(target.x, target.y + 1)
                if t:
                    game.player.fighter.attack(t, player=True, game=game)
                    t = None
                t = game.check_for_target(target.x - 1, target.y - 1)
                if t:
                    game.player.fighter.attack(t, player=True, game=game)"""

    def take_damage(self, damage, attacker, game):
        # apply damage if possible
        if damage > 0 and self.hp > 0:
            self.hp -= damage
            self.owner.flashing = True
            self.owner.flash_duration = 1
            r = libtcod.random_get_int(0, 0, 100)
            if r > 75:
                r = libtcod.random_get_int(0, 0, len(bark.hit_barks)-1)
                b = bark.Bark(game.gEngine, game.dungeon_console, self.owner, 1.0, bark.hit_barks[r])
                game.bark_manager.add_bark(b)

            # check for death. if there's a death function, call it
            if self.hp <= 0:
                attacker.fighter.current_xp += self.current_xp
                function = self.death_function
                if function is not None:
                    function(self.owner)
            else:
                pass  # flash  \ (. )( .) /

    def heal(self, amount):
        # heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.stat.get_stat_base("HP"):
            self.hp = self.stat.get_stat_base("HP")


class Torch:    # TODO REFACTOR move torch to item.py
    def __init__(self, owner):
        self.owner = owner
        #self.light_source = self.owner.fighter.gear.light_source

    def render(self, game, gEngine):
        if self.owner.fighter.gear.light_source:
            if self.owner.fighter.gear.light_source.item.equipment.fuel > 0:
                r = libtcod.random_get_float(0, -0.025, 0.025)
                v = self.owner.fighter.gear.light_source.item.equipment.torch_intensity + r
                c = self.owner.fighter.gear.light_source.item.equipment.torch_color
                r = c[0] / 255 * v
                g = c[1] / 255 * v
                b = c[2] / 255 * v

                gEngine.lightmask_add_light(self.owner.x, self.owner.y, (r, g, b))

    def update(self, game):

        if self.owner.fighter.gear.light_source:
            if self.owner.fighter.gear.light_source.item.equipment.fuel > 1:
                self.owner.fighter.gear.light_source.item.equipment.fuel -= 1
            else:
                m = "%s has burned out and is discarded!"%(self.owner.fighter.gear.light_source.name.capitalize())
                game.message.message(m)
                self.owner.fighter.gear.light_source = None





# x,y offsets for co-ords next to the player
offsets = [(1, 0), (0, 1), (-1, 0), (0, -1),
           (1, 1), (-1, 1), (-1, -1), (1, -1)]


def get_next_to_player(mob, player, map):
    d = 100
    dx, dy = 0, 0
    for i in range(len(offsets)):
        px, py = offsets[i]
        if mob.owner.distance(player.x + px, player.y + py) < d:
            if not mob.owner.is_blocked(player.x + px, player.y + py, map, mob.owner.objects):
                dx, dy = player.x + px, player.y + py
                d = mob.owner.distance(player.x + px, player.y + py)
    return dx, dy


    ## TODO REFACTOR move AI class and functions to their own package

class AI_Base:
    def __init__(self):
        self.node = None
        self.owner = None
        self.found_player = False

    def remove_from_node(self):
        self.node.remove_from_group(self.owner)

    def add_node(self, node):
        self.node = node


class BasicMonster(AI_Base):
    # AI for a basic monster.
    def take_turn(self, game):
        # a basic monster takes its turn. if you can see it, it can see you
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.stat.get_stat("Speed"), self.owner)
        if libtcod.map_is_in_fov(game.fov, self.owner.x, self.owner.y):
            # move towards player if far away
            if self.owner.distance_to(game.player) >= 2:
                # we need to get the closest distance from the monster, surrounding the player
                dx, dy = get_next_to_player(self, game.player, game.level.dungeon)
                # then move to it
                if libtcod.path_compute(game.path, self.owner.x, self.owner.y, dx, dy):
                    x, y = libtcod.path_walk(game.path, True)
                    self.owner.x = x
                    self.owner.y = y

                    # close enough, attack! (if the player is still alive.)
            elif game.player.fighter.hp > 0:
                self.owner.fighter.attack(game.player, force_attack=True)
            #     direction = None
            #     if self.owner.x < game.player.x and self.owner.y == game.player.y:
            #         direction = 'east'
            #     elif self.owner.x > game.player.x and self.owner.y == game.player.y:
            #         direction = 'west'
            #     elif self.owner.y < game.player.y and self.owner.x == game.player.x:
            #         direction = 'south'
            #     elif self.owner.y > game.player.y and self.owner.x == game.player.x:
            #         direction = 'north'
            #     if direction:
            #         self.owner.fighter.attack(game.player, direction=direction, game=game)
        else:  # start wandering
            self.owner.ai = WanderingMonster(x=self.owner.x, y=self.owner.y)
            self.owner.ai.owner = self.owner


class WanderingMonster(AI_Base):
    # Ai for a monster to randomly wander around when not in the view of the player
    def __init__(self, radius=3, x=1, y=1):
        self.radius = radius
        self.dest = False
        self.home_x = x
        self.home_y = y

        AI_Base.__init__(self)

    def take_turn(self, game):
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.stat.get_stat("Speed"), self.owner)

        if self.dest and self.owner.distance(self.dest_x, self.dest_y) <= 0:
            self.dest = False

        if self.dest and self.owner.distance(self.dest_x, self.dest_y) > 0:
            self.owner.move_towards(self.dest_x, self.dest_y, game.Map.map, game.objects)

        if not self.dest:
            picked = False
            while not picked:
                min_x = self.home_x - self.radius
                max_x = self.home_x + self.radius

                min_y = self.home_y - self.radius
                max_y = self.home_y + self.radius

                mx, my = game.dungeon_width, game.dungeon_height
                if max_x > mx:
                    max_x = mx
                if max_y > my:
                    max_y = my
                if min_x <= 0:
                    min_x = 1
                if min_y <= 0:
                    min_y = 1
                # make sure min and max values are within the boundaries of the map
                self.dest_x = libtcod.random_get_int(0, min_x, max_x)
                self.dest_y = libtcod.random_get_int(0, min_y, max_y)
                if self.dest_x >= game.dungeon_width:
                    self.dest_x = game.dungeon_width-1
                if self.dest_y >= game.dungeon_height:
                    self.dest_y = game.dungeon_height-1

                if not game.level.dungeon[self.dest_x][self.dest_y].blocked:
                    if not self.owner.distance(self.dest_x, self.dest_y) == 0:
                        picked = True

            self.owner.move_towards(self.dest_x, self.dest_y, game.level.dungeon, game.objects)

        if libtcod.map_is_in_fov(game.fov, self.owner.x, self.owner.y):
            node = self.owner.ai.node
            self.owner.ai = BasicMonster()
            self.owner.ai.owner = self.owner
            self.owner.ai.node = node
            if not self.owner.ai.found_player:
                will_bark = libtcod.random_get_int(0, 0, 100)
                if will_bark >=  75:
                    bark_number = libtcod.random_get_int(0, 1, len(bark.player_found_barks)-1)
                    b = bark.Bark(game.gEngine, game.dungeon_console, self.owner, 2.5, bark.player_found_barks[bark_number], True)
                    game.bark_manager.add_bark(b)
                # add a bark here
                self.owner.ai.found_player = True



class ConfusedMonster(AI_Base):
    # AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=3):
        self.old_ai = old_ai
        self.num_turns = num_turns
        self.node = old_ai.node
        AI_Base.__init__(self)

    def take_turn(self, game):
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.stat.get_stat("Speed"), self.owner)
        if self.num_turns > 0:  # still confused...
            # move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1), game.level.dungeon,
                            game.objects)
            self.num_turns -= 1

        else:  # restore the previous AI
            self.owner.ai = self.old_ai
            self.owner.message.message('The ' + self.owner.name + ' is no longer confused!', 2)


class RangedMonster(AI_Base):
    # AI for a ranged type monster
    def take_turn(self, game):
        # a mage takes its turn; if you can see it, it can see you.
        if libtcod.map_is_in_fov(game.fov_map, self.owner.x, self.owner.y):

            # move towards plaer if far away
            if self.owner.fighter.type == 'mage':
                if self.owner.distance_to(game.player) >= spell.max_range:
                    self.owner.move_towards(game.player.x, game.player.y, game.level.dungeon, game.objects)
                else:
                    # cast spell
                    pass
            if self.owner.fighter.type == 'ranged':
                if self.owner.distance_to(game.player) >= weapon.max_range:
                    self.owner.move_towards(game.player.x, game.player.y, game.level.dungeon, game.objects)
                else:
                    # ranged attack
                    pass

            # close enough, cast spell


def monster_death(monster):
    if monster.ai.node:
        monster.ai.remove_from_node()
    # drop all of equipped gear from monsters
    for item in [monster.fighter.gear.gimmie_da_weapon(), monster.fighter.gear.gimmie_da_weapon(off_hand=True)]:
        if item:
            if item.item.equipment.type != 'monster_melee':
                monster.fighter.inventory.append(item)
    for item in monster.fighter.gear.gimmie_da_armors():
        if item:
            monster.fighter.inventory.append(item)
    for item in monster.fighter.inventory:
        item.item.drop(monster.fighter.inventory, monster, False)
        item.send_to_back()
    # Add loot drops
    # Add gore
    monster.fighter.ticker.remove_object(monster)
    monster.message.message(monster.name.capitalize() + ' is dead!', 5)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()
