__author__ = 'GrishdaFish'

# After creating a new font tile, add the name of the tile, and use the next available int
# Call these to use new font by using chr(long_sword)
long_sword = 256
dagger = 257
short_sword = 258
great_sword = 259
mace = 260
hammer = 261
battle_axe = 262
bow_and_arrow = 263
bow = 264


# Add new font tiles here, with the x, y co-ords (in tiles) from upper left corner (0, 0)
Fonts = {
    long_sword: (0, 5),
    dagger: (1, 5),
    short_sword: (2, 5),
    great_sword: (3, 5),
    mace: (4, 5),
    hammer: (5, 5),
    battle_axe: (6, 5),
    bow_and_arrow: (0, 6),
    bow: (1, 6),
}