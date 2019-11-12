import sys
import os
import toml


class GameOptions:
    def __init__(self):
        self.options = open(os.path.join(sys.path[0], 'options.toml')).read()

        self.fullscreen = False
        self.key_set = None
        self.fps = None

        self.key_north = None
        self.key_east = None
        self.key_south = None
        self.key_west = None
        self.key_inventory = None
        self.key_pickup = None
        self.key_equip = None
        self.key_help = None
        self.key_drop = None
        self.key_character = None

        self.load_options()

        #self.options.close()

    def load_options(self):
        options = toml.loads(self.options)
        game_options = options.get('game_options')
        self.setup_game_options(game_options)

        key_options = options.get('keys')
        self.setup_key_config(key_options)

    def setup_game_options(self, game_options):
        self.fullscreen = game_options.get('fullscreen')
        self.key_set = game_options.get('key_set')
        self.fps = game_options.get('fps')

    def setup_key_config(self, key_options):
        keys = key_options.get(self.key_set)
        self.key_north = keys.get('key_north')
        self.key_east = keys.get('key_east')
        self.key_south = keys.get('key_south')
        self.key_west = keys.get('key_west')
        self.key_inventory = keys.get('key_inventory')
        self.key_pickup = keys.get('key_pickups')
        self.key_equip = keys.get('key_equip')
        self.key_help = keys.get('key_help')
        self.key_drop = keys.get('key_drop')
        self.key_character = keys.get('key_character')

