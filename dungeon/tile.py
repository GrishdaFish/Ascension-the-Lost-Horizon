import tcod as libtcod

# Variables for tile bitmasking
tile_bitshift = 4
tile_bit_offset = 31


class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked=True, block_sight=None):
        self.blocked = blocked
        # all tiles start unexplored
        self.explored = False
        self.tile = '#'
        self.spawn_node = False
        self.opacity = 1.0
        self.color = libtcod.Color(99, 99, 99)
        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

    def set_color(self, col):
        self.color = col

    # Thanks to my friend Art for help with this bitmasking stuff.
    def return_bitmask(self):
        bit_mask_values = {',': 1, '.': 2, '`': 4, "'": 8, '#': 16}  # dictionary for tiles and respective bits
        ##sets the bits on or off based on if its true or false
        tilemask = (self.blocked * 1) | (self.block_sight * 2) | (self.explored * 4) | (self.spawn_node * 8)
        ##Shift the bitmask over, incase new bools are added in front.
        ##Should keep old maps compatable
        tilemask = tilemask | bit_mask_values[self.tile] << tile_bitshift  ##gets the bit for the tile char, then shifts over
        return tilemask

    def build_from_bitmask(self, bitmask):
        bit_unmask_values = {1: ',', 2: '.', 4: '`', 8: "'", 16: '#'}
        self.blocked = bool((bitmask & 1) * True)
        self.block_sight = bool((bitmask & 2) * True)
        self.explored = bool((bitmask & 4) * True)
        self.spawn_node = bool((bitmask & 8) * True)
        self.tile = bit_unmask_values[(bitmask >> tile_bitshift) & tile_bit_offset]