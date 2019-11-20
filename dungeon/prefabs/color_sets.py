import tcod as libtcod

ground_colors = libtcod.color_gen_map([libtcod.desaturated_green, libtcod.darker_green], [0, 5])
wall_colors = libtcod.color_gen_map([libtcod.light_grey, libtcod.lightest_grey], [0, 5])
floor_colors = libtcod.color_gen_map([libtcod.light_sepia, libtcod.lighter_sepia], [0, 5])
colorset_town = {
    'ground': ground_colors,
    'wall': wall_colors,
    'floor': floor_colors
}