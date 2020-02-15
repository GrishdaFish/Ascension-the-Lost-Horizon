__author__ = 'GrishdaFish'
import tcod as libtcod
# After creating a new font tile, add the name of the tile, and use the next available int
# Call these to use new font by using chr(long_sword)

# TODO ALWAYS PLACE THE NEXT AVAILABLE NUMBER HERE WHEN YOU ARE DONE EDITING!
#  next usable number is: 294
# melee weapons
long_sword = 256
dagger = 257
short_sword = 258
great_sword = 259
mace = 260
hammer = 261
two_handed_hammer = 265
hand_axe = 266
battle_axe = 262
shield = 293

# ranged weapons
bow_and_arrow = 263
bow = 264
throwing_axe = 267
javelen = 268

# consumables
big_potion = 269
small_potion = 270
scroll = 271

# armor
helm = 283
glove = 284
boot = 285
torso = 286
cloak = 287
ring = 288
neck = 289
shoulder = 290
arms = 291
legs = 292

# Libtcod TCOD Font fixes
CHAR_ARROW_N = 272
CHAR_ARROW_S = 273
CHAR_ARROW_E = 274
CHAR_ARROW_W = 275
CHAR_ARROW2_N = 276
CHAR_ARROW2_S = 278
CHAR_ARROW2_E = 279
CHAR_ARROW2_W = 280
CHAR_DARROW_H = 281
CHAR_DARROW_V = 282


# Add new font tiles here, with the x, y co-ords (in tiles) from upper left corner (0, 0)
Fonts = {
    CHAR_ARROW_N: (0, 2),
    CHAR_ARROW_S: (1, 2),
    CHAR_ARROW_E: (2, 2),
    CHAR_ARROW_W: (3, 2),
    CHAR_ARROW2_N: (4, 2),
    CHAR_ARROW2_S: (5, 2),
    CHAR_ARROW2_E: (6, 2),
    CHAR_ARROW2_W: (7, 2),
    CHAR_DARROW_H: (8, 2),
    CHAR_DARROW_V: (9, 2),
    long_sword: (0, 5),
    dagger: (1, 5),
    short_sword: (2, 5),
    great_sword: (3, 5),
    mace: (4, 5),
    hammer: (5, 5),
    two_handed_hammer: (6, 5),
    hand_axe: (7, 5),
    battle_axe: (8, 5),
    bow_and_arrow: (0, 6),
    bow: (1, 6),
    throwing_axe: (2, 6),
    javelen: (3, 6),
    big_potion: (0, 7),
    small_potion: (1, 7),
    scroll: (2, 7),
    helm: (10, 5),
    glove: (11, 5),
    boot: (12, 5),
    torso: (13, 5),
    cloak: (14, 5),
    ring: (15, 5),
    neck: (16, 5),
    shoulder: (17, 5),
    arms: (18, 5),
    legs: (19, 5),
    shield: (9, 5),
}
