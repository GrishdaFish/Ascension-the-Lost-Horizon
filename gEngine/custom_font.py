__author__ = 'GrishdaFish'
import os
import toml

path = os.path.abspath('.')
custom_font = os.path.join(path, 'custom_font.toml')
class CustomFontOptions:
    def __init__(self):
        f = open(custom_font)
        font = f.read()
        f.close()
        font = toml.loads(font)

        self.fonts = []
        data = font.get('data')
        print(data)
        print("Loading font data")

        self.starting_id = data.get('starting_id')
        self.font_size = data.get('font_size')
        self.file_width = data.get('file_width')
        self.file_height = data.get('file_height')
        print('Data loaded')
        print("loading fonts")

        fonts = font.get('custom_font')
        font_id = self.starting_id
        for f in fonts:
            cf = Font()
            cf.name = f.get("name")
            cf.location = f.get("location")
            cf.id = font_id
            font_id += 1
            self.fonts.append(cf)
        print("Fonts loaded")

class Font:
    def __init__(self):
        self.name = ""
        self.location = []
        self.id = 0


# After creating a new font tile, add the name of the tile, and use the next available int
# Call these to use new font by using chr(long_sword)

# TODO ALWAYS PLACE THE NEXT AVAILABLE NUMBER HERE WHEN YOU ARE DONE EDITING!
#  next usable number is: 374

# pot slingah custom
shovel = 304
bomb = 305
buff_hp = 306
debuff_hp = 307
buff_str = 308
debuff_str = 309
beast = 310
lava_monster = 311
bull_demon = 312
scale = 313
money_bag = 314
stalag_a = 315
stalag_b = 316
stalag_c = 317
stalac_a = 318
stalac_b = 319
stalac_c = 320
pillar_top = 321
pillar_bottom = 322
rocks_a = 323
rocks_b = 324
rocks_c = 325
rocks_d = 326

# dungeon 2 greebs, crypt ==========
headstone_a = 359
headstone_b = 360
headstone_c = 361
headstone_d = 362
headstone_e = 363
headstone_f = 364
headstone_g = 365
bone_pile_a = 366
bone_pile_b = 367
bone_pile_c = 368
shrine = 369
webs_a = 370
webs_b = 371
webs_c = 372
webs_d = 373

# FAT ICONS ============
boulder_1a = 327
boulder_1b = 328
boulder_1c = 329
boulder_1d = 330
esc_menu_a = 331
esc_menu_b = 332
esc_menu_c = 333
esc_menu_d = 334
fat_pot_a = 335
fat_pot_b = 336
fat_pot_c = 337
fat_pot_d = 338
fat_shovel_a = 339
fat_shovel_b = 340
fat_shovel_c = 341
fat_shovel_d = 342
fat_bow_a = 343
fat_bow_b = 344
fat_bow_c = 345
fat_bow_d = 346
fat_hammer_a = 347
fat_hammer_b = 348
fat_hammer_c = 349
fat_hammer_d = 350
fat_q_a = 351
fat_q_b = 352
fat_q_c = 353
fat_q_d = 354
lava_pit_a = 355
lava_pit_b = 356
lava_pit_c = 357
lava_pit_d = 358

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
spear = 299
flail = 300
staff = 301

# ranged weapons
bow_and_arrow = 263
bow = 264
throwing_axe = 267
javelin = 268
sling = 294
xbow = 295

# ammo
arrow = 296
bolt = 297
quiver = 298

# consumables
big_potion = 269
small_potion = 270
scroll = 271
lantern = 302
torch = 303

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
    'CHAR_ARROW_N': (0, 2),
    'CHAR_ARROW_S': (1, 2),
    'CHAR_ARROW_E': (2, 2),
    'CHAR_ARROW_W': (3, 2),
    'CHAR_ARROW2_N': (4, 2),
    'CHAR_ARROW2_S': (5, 2),
    'CHAR_ARROW2_E': (6, 2),
    'CHAR_ARROW2_W': (7, 2),
    'CHAR_DARROW_H': (8, 2),
    'CHAR_DARROW_V': (9, 2),

    'long_sword': (0, 5),
    'dagger': (1, 5),
    'short_sword': (2, 5),
    'great_sword': (3, 5),
    'mace': (4, 5),
    'hammer': (5, 5),
    'two_handed_hammer': (6, 5),
    'hand_axe': (7, 5),
    'battle_axe': (8, 5),

    'bow_and_arrow': (0, 6),
    'bow': (1, 6),
    'throwing_axe': (2, 6),
    'javelin': (3, 6),

    'big_potion': (0, 7),
    'small_potion': (1, 7),
    'scroll': (2, 7),

    'helm': (10, 5),
    'glove': (11, 5),
    'boot': (12, 5),
    'torso': (13, 5),
    'cloak': (14, 5),
    'ring': (15, 5),
    'neck': (16, 5),
    'shoulder': (17, 5),
    'arms': (18, 5),
    'legs': (19, 5),
    'shield': (9, 5),

    'sling': (4, 6),
    'xbow': (5, 6),
    'arrow': (3, 7),
    'bolt': (4, 7),
    'quiver': (5, 7),
    'flail': (6, 6),
    'staff': (7, 6),
    'spear': (8, 6),
    'lantern': (6, 7),
    'torch': (7, 7),

    'shovel': (10, 7),
    'bomb': (9, 7),
    'buff_hp': (11, 7),
    'debuff_hp': (13, 7),
    'buff_str': (12, 7),
    'debuff_str': (14, 7),
    'beast': (11, 6),
    'lava_monster': (12, 6),
    'bull_demon': (13, 6),
    'scale': (15, 6),
    'money_bag': (14, 6),

    'stalag_a': (3, 9),
    'stalag_b': (4, 9),
    'stalag_c': (5, 9),
    'stalac_a': (3, 8),
    'stalac_b': (4, 8),
    'stalac_c': (5, 8),
    'pillar_top': (2, 8),
    'pillar_bottom': (2, 9),
    'rocks_a': (6, 8),
    'rocks_b': (7, 8),
    'rocks_c': (8, 8),
    'rocks_d': (9, 8),
    'boulder_1a': (0, 8),
    'boulder_1b': (1, 8),
    'boulder_1c': (0, 9),
    'boulder_1d': (1, 9),
    'esc_menu_a': (20, 6),
    'esc_menu_b': (21, 6),
    'esc_menu_c': (20, 7),
    'esc_menu_d': (21, 7),
    'fat_pot_a': (22, 6),
    'fat_pot_b': (23, 6),
    'fat_pot_c': (22, 7),
    'fat_pot_d': (23, 7),
    'fat_shovel_a': (24, 6),
    'fat_shovel_b': (25, 6),
    'fat_shovel_c': (24, 7),
    'fat_shovel_d': (25, 7),
    'fat_bow_a': (26, 6),
    'fat_bow_b': (27, 6),
    'fat_bow_c': (26, 7),
    'fat_bow_d': (27, 7),
    'fat_hammer_a': (28, 6),
    'fat_hammer_b': (29, 6),
    'fat_hammer_c': (28, 7),
    'fat_hammer_d': (29, 7),
    'fat_q_a': (30, 6),
    'fat_q_b': (31, 6),
    'fat_q_c': (30, 7),
    'fat_q_d': (31, 7),
    'lava_pit_a': (1, 10),
    'lava_pit_b': (2, 10),
    'lava_pit_c': (1, 11),
    'lava_pit_d': (2, 12),

    'headstone_a': (0, 10),
    'headstone_b': (1, 10),
    'headstone_c': (2, 10),
    'headstone_d': (3, 10),
    'headstone_e': (4, 10),
    'headstone_f': (5, 10),
    'headstone_g': (6, 10),
    'bone_pile_a': (0, 11),
    'bone_pile_b': (1, 11),
    'bone_pile_c': (3, 11),
    'shrine': (2, 11),
    'webs_a': (4, 11),
    'webs_b': (5, 11),
    'webs_c': (6, 11),
    'webs_d': (7, 11),
}

if __name__ == "__main__":
    f = open(custom_font, "w")
    data_header = ['[data]',
                   '    starting_id = 256 # The first available id for custom fonts. Depends on your own font file' ,
                   '    font_size = [16, 16] # Font size in Pixels',
                   '    file_width = 32 # Number of characters wide the file is',
                   '    file_height = 12 # Number of characters high the file is'
                   ]
    for line in data_header:
        f.write(line + '\n')
    f.write('\n')

    for key, val in Fonts.items():
        print("Dict Vals: %s, %s"%(str(key), str(val)))
        f.write('[[custom_font]]'+'\n')
        f.write('   name = "%s" # Unique String Name'%key + '\n')
        f.write('   location = [%d, %d] # [X, Y] location in the font file. [0, 0] is upper left corner [COLUMN, ROW]'%(val[0], val[1]) + '\n\n')
    f.close()