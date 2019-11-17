import math
from game import lights
import tcod as libtcod

def fire_shot(ox, oy, dx, dy, shooter, game, target=None):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))

    ddx = math.cos(angle * 1.0)
    ddy = math.sin(angle * 1.0)

    final_x = ox + ddx * 1.0
    final_y = oy + ddy * 1.0

    i = libtcod.random_get_float(0, 1.0, 1.15)
    l = lights.Light(int(final_x), int(final_y), game.light_handler, 1.0, 0.05, i)
    game.light_handler.add_light(l)
    if target:
        if shooter == game.player:
            shooter.fighter.ranged_targeted_attack(target, True, game)
        else:
            shooter.fighter.ranged_targeted_attack(target, False, game)
    else:
        blind_fire(dx, dy, ox, oy, game, shooter)



def blind_fire(dx, dy, ox, oy, game, shooter):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))

    ddx = math.cos(angle * 1.0)
    ddy = math.sin(angle * 1.0)
    final_x = ox + ddx
    final_y = oy + ddy
    target = None
    while True:
        target = game.check_for_target(int(final_x), int(final_y))
        if target:
            break
        if game.level.dungeon[int(final_x)][int(final_y)].blocked:
            game.message.message('hit wall')
            i = libtcod.random_get_float(0, 0.65, 0.85)
            l = lights.Light(int(final_x-ddx), int(final_y-ddy), game.light_handler, 2.0, 0.05, i)
            game.light_handler.add_light(l)
            break
        final_x += ddx * 1.0
        final_y += ddy * 1.0

    if target:
        if shooter == game.player:
            shooter.fighter.ranged_targeted_attack(target, True, game)
        else:
            shooter.fighter.ranged_targeted_attack(target, False, game)

