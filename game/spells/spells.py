__author__ = 'GrishdaFish'
import tcod as libtcod
from gEngine import lights
from gEngine.utilities import dijikstra_map
from game.object import object
from game.object import item
from game import render
from game.spells import spell_effects
import time

class Spell:
    def __init__(self, min=0, max=0, range=0, radius=0, targets=0, ef_type=None, ad_eff=None, spel_eff=None,
                 eff_col=None):
        self.min = min
        self.max = max
        self.range = range
        self.radius = radius
        self.targets = targets
        self.type = ef_type
        self.effect_type = spells[ef_type]

        self.addition_effects = ad_eff
        self.spell_effects = spel_eff
        self.effect_color = eff_col

    def cast(self, target, player, game=None):
        if self.effect_type:
            return self.effect_type(self.min, self.max, self.range, self.radius, self.targets, target, player, game, self.effect_color)


def heal(min, max, range, radius, targets, target, player, game, effect_color):
    # heal the player
    if target == game.player:
        if target.fighter.hp == target.fighter.stat.get_stat_base("HP"):
            game.message.message('You are already at full health.', libtcod.cyan)
            return 'cancelled'
        l = lights.Light(target.x, target.y, game.light_handler, decay=0.025, flicker=True, intensity=1.0, color=libtcod.lime)
        game.level.light_handler.add_light(l)
        game.message.message('Your wounds start to feel better!', libtcod.light_lime)
    HEAL_AMOUNT = libtcod.random_get_int(0, min, max)
    target.fighter.heal(HEAL_AMOUNT)


def fireball(min, max, range, radius, targets, target, player, game, effect_color):
    # ask the player for a target tile to throw a fireball at
    game.message.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_azure)
    (x, y) = target_tile(game, range, radius)
    if x is None:
        game.message.message('You cancelled the spell!', libtcod.light_cyan)
        return 'cancelled'
    game.message.message('The fireball explodes, burning everything within ' + str(radius) + ' tiles!', 5)
    #game.gEngine.particle_explosion(5, x, y, b=True, color=libtcod.red)
    l = lights.Light(x, y, game.light_handler, flicker=True, flicker_intensity=0.15)
    c = [libtcod.white, libtcod.flame]
    l.staged_lerp(2.0, 1.2, 0.075, 0.0075, c)
    game.level.light_handler.add_light(l)
    FIREBALL_DAMAGE = libtcod.random_get_int(0, min, max)
    if game.objects:
        for obj in game.objects:  # damage every fighter in range, including the player
            if obj.distance(int(x), int(y)) <= radius and obj.fighter:
                game.message.message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.',
                                     libtcod.light_crimson)
                obj.fighter.take_damage(FIREBALL_DAMAGE, player, game)


def lightning(min, max, range, radius, targets, target, player, game, effect_color):
    # find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(game, range)
    if monster is None:  # no enemy found within maximum range
        game.message.message('No enemy is close enough to strike.', libtcod.light_cyan)
        return 'cancelled'
    l = lights.Light(monster.x, monster.y, game.light_handler, flicker=True)
    c = [libtcod.white, libtcod.light_blue]
    l.staged_lerp(2.0, 1.0, 0.05, 0.0095, c)
    game.level.light_handler.add_light(l)
    lightning_damage = libtcod.random_get_int(0, min, max)
    game.message.message('A lighting bolt strikes the ' + monster.name +
                         ' with a loud thunder! The damage is '
                         + str(lightning_damage) + ' hit points.', libtcod.light_crimson)
    monster.fighter.take_damage(lightning_damage, player, game)

    # draw the effect
    #game.gEngine.particle_projectile(1, player.x, player.y, monster.x, monster.y, color=libtcod.lightest_blue)
    # spell_effects.path_effect(game,player.x,player.y,monster.x,monster.y,5)


def chain_lightning(min, max, r, radius, targets, target, player, game, effect_color):
    num_chains = libtcod.random_get_int(0, 1, radius)
    monster = closest_monster(game, r)
    # blast with lightning
    if monster is None:  # no enemy found within maximum range
        game.message.message('No enemy is close enough to strike.', libtcod.light_cyan)
        return 'cancelled'
    l = lights.Light(monster.x, monster.y, game.light_handler, flicker=True)
    c = [libtcod.white, libtcod.light_blue]
    l.staged_lerp(2.0, 1.0, 0.05, 0.0095, c)
    game.level.light_handler.add_light(l)
    lightning_damage = libtcod.random_get_int(0, min, max)
    game.message.message('A lighting bolt strikes the ' + monster.name +
                         ' with a loud thunder! The damage is '
                         + str(lightning_damage) + ' hit points.', libtcod.light_crimson)
    monster.fighter.take_damage(lightning_damage, player, game)
    for x in range(num_chains):
        monster = closest_target(game, r-1, monster)  # get the next closest target to the first target
        if monster is None:  # no enemy found within maximum range
            game.message.message('No enemy is close enough to chain to.', libtcod.light_cyan)
            return
        l = lights.Light(monster.x, monster.y, game.light_handler, flicker=True)
        c = [libtcod.white, libtcod.light_blue]
        l.staged_lerp(2.0, 1.0, 0.05, 0.0095, c)
        game.level.light_handler.add_light(l)
        lightning_damage = libtcod.random_get_int(0, min, max)
        if monster == game.player:
            game.message.message('You get blasted by your own spell!', libtcod.red)
        else:
            game.message.message('The lighting bolt chains and strikes the ' + monster.name +
                                 ' with a loud thunder! The damage is '
                                 + str(lightning_damage) + ' hit points.', libtcod.light_crimson)
        monster.fighter.take_damage(lightning_damage, player, game)


def confuse(min, max, range, radius, targets, target, player, game, effect_color):
    # ask the player for a target to confuse
    game.message.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(game, range)
    if monster is None:
        game.message.message('You cancelled the spell!', libtcod.cyan)
        return 'cancelled'
    l = lights.Light(monster.x, monster.y, game.light_handler, flicker=True, intensity=1.35, decay=0.0005)
    l.randomize()
    game.level.light_handler.add_light(l)
    numturns = libtcod.random_get_int(0, min, max)
    # replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = object.ConfusedMonster(old_ai, num_turns=numturns)
    monster.ai.owner = monster  # tell the new component who owns it
    game.message.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!',
                         libtcod.light_pink)


def light(min, max, range, radius, targets, target, player, game, effect_color):
    i = libtcod.random_get_float(0, min, max)
    equip_component = item.Equipment(type='light_source', fuel=range+1, color=effect_color, intensity=i)
    item_component = item.Item(equipment=equip_component)
    item_component.stackable = False
    item_component.value = int(0)
    equip = object.Object(game.dungeon_console, 0, 0, ' ', 'magical light', effect_color, item=item_component)
    equip.message = game.message
    equip.objects = game.objects
    if target == game.player:
        game.message.message("You are surrounded by a glowing magical light!", libtcod.light_cyan)
        if target.fighter.gear.light_source:
            if target.fighter.gear.light_source.name == "magical light":
                game.message.message("You cannot cast magical light while under the effects of another magical light!", libtcod.flame)
                return "cancelled"
            else:
                target.fighter.inventory.append(target.fighter.gear.light_source)
        target.fighter.gear.light_source = equip


def detect_monsters(min, max, range, radius, targets, target, player, game, effect_color):
    num_turns = libtcod.random_get_int(0, min, max)
    if game.monster_force_display[0]:
        game.monster_force_display[1] += num_turns
        game.message.message("You've extended your ability to see all monsters around you by " + str(num_turns) +
                             " turns!", libtcod.light_cyan)
    else:
        game.monster_force_display[0] = True
        game.monster_force_display[1] = num_turns
        game.message.message("You can now see all monsters around you for " + str(num_turns) +
                             " turns!", libtcod.light_cyan)


def detect_loot(min, max, range, radius, targets, target, player, game, effect_color):
    num_turns = libtcod.random_get_int(0, min, max)
    if game.loot_force_display[0]:
        game.loot_force_display[1] += num_turns
        game.message.message("You've extended your ability to see all items around you by " + str(num_turns) +
                             " turns!", libtcod.light_cyan)
    else:
        game.loot_force_display[0] = True
        game.loot_force_display[1] = num_turns
        game.message.message("You can now see all items around you for " + str(num_turns) +
                             " turns!", libtcod.light_cyan)


def magical_mapping(min, max, range, radius, targets, tile, player, game, effect_color):
    for tile in game.level.dungeon:
        tile.explored = True



def detect_monsters(min, max, range, radius, targets, target, player, game, effect_color):
    num_turns = libtcod.random_get_int(0, min, max)
    if game.monster_force_display[0]:
        game.monster_force_display[1] += num_turns
        game.message.message("You've extended your ability to see all monsters around you by " + str(num_turns) +
                             " turns!", libtcod.light_cyan)
    else:
        game.monster_force_display[0] = True
        game.monster_force_display[1] = num_turns
        game.message.message("You can now see all monsters around you for " + str(num_turns) +
                             " turns!", libtcod.light_cyan)


def detect_loot(min, max, range, radius, targets, target, player, game, effect_color):
    num_turns = libtcod.random_get_int(0, min, max)
    if game.loot_force_display[0]:
        game.loot_force_display[1] += num_turns
        game.message.message("You've extended your ability to see all items around you by " + str(num_turns) +
                             " turns!", libtcod.light_cyan)
    else:
        game.loot_force_display[0] = True
        game.loot_force_display[1] = num_turns
        game.message.message("You can now see all items around you for " + str(num_turns) +
                             " turns!", libtcod.light_cyan)


def magical_mapping(min, max, range, radius, targets, tile, player, game, effect_color):
    for tile in game.level.dungeon:
        tile.explored = True


spells = {
    'heal': heal,
    'fireball': fireball,
    'light': light,
    'chain lightning': chain_lightning,
    'lightning': lightning,
    'confusion': confuse,
    'confuse': confuse,
    'detect monster': detect_monsters,
    'detect items': detect_loot,
    'none': None,
    '': None,
    None: None,
}


##Targeting for spells
def target_monster(game, max_range=None):
    # returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(game, max_range)
        if x is None:  # player cancelled
            return None

        # return the first clicked monster, otherwise continue looping
        for obj in game.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != game.player:
                return obj

def closest_target(game, max_range, target):
    close_target = None
    closest_dist = max_range + 1
    for object in game.objects:
        if object.fighter:
            if object != target:
                dist = target.distance_to(object)
                if dist < closest_dist:
                    close_target = object
                    closest_dist = dist
    return close_target

def closest_monster(game, max_range):
    # find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  # start with (slightly more than) maximum range
    for object in game.objects:
        if object.fighter and libtcod.map_is_in_fov(game.fov, object.x, object.y):
            if object != game.player:
                # calculate distance between this object and the player
                dist = game.player.distance_to(object)
                if dist < closest_dist:  # it's closer, so remember it
                    closest_enemy = object
                    closest_dist = dist
    return closest_enemy


def target_tile(game, max_range=None, radius=None):
    if not radius:
        radius = 1
    targeting_window = TargetRender(radius, game.dungeon_console, game)
    renderers = [targeting_window.render]
    game.gEngine.handle_input(clear=True)
    time.sleep(0.5)
    while True:

        render.render_all(game, renderers)
        game.gEngine.console_flush()
        key, mouse = game.gEngine.handle_input()
        # libtcod.console_flush()
        # key = libtcod.Key()
        # mouse = libtcod.Mouse()
        # libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
        x, y = (mouse.cx-int(radius/2)-1, mouse.cy-int(radius/2)-1)
        if mouse.rbutton or key.vk == libtcod.KEY_ESCAPE:
            return None, None  # cancel if the player right-clicked or pressed Escape

        # accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton and game.gEngine.map_is_in_fov(x, y) and
                (max_range is None or game.player.distance(x, y) <= max_range)):
            return x, y


class TargetRender:
    def __init__(self, radius, target_console, game):
        self.radius = radius
        self.target_console = target_console
        self.targeting_window = game.gEngine.console_new(radius + 2, radius + 2)

    def render(self, game):
        # key = libtcod.Key()
        #         # mouse = libtcod.Mouse()
        #         # libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
        key, mouse = game.gEngine.handle_input()
        x, y = (mouse.cx, mouse.cy)
        r, g, b = libtcod.white
        game.gEngine.console_set_default_background(self.targeting_window, r, g, b)
        game.gEngine.console_print_frame(self.targeting_window, 0, 0, self.radius + 2, self.radius + 2, True)
        game.gEngine.console_blit(self.targeting_window, 0, 0, 0, 0, self.target_console,
                                  x - int(self.radius / 2) - 2, y - int(self.radius / 2) - 2, 0.5, 0.5)

def line_listener(x, y):
    pass


def path_listener(x, y):
    pass
