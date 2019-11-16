import os
import sys
import toml
from gEngine import gEngine
font = os.path.join(sys.path[0], 'terminal10x10_gs_tc.png')


class EngineConfig:
    def __init__(self):
        self.screen_width = None
        self.screen_height = None
        self.font = None
        self.font_name = None
        self.renderer = None
        self.name = None
        self.version = None
        self.font_layout = None
        self.font_type = None

        self.setup_config_default()
        self.load_config()

    def load_config(self):
        if gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        with open(os.path.join(path, 'gEngine', 'config.toml')) as config:
            config = config.read()
            config = toml.loads(config)
            config = config.get('engine_config')
            self.screen_width = config.get('screen_width')
            self.screen_height = config.get('screen_height')
            self.font_name = config.get('font')
            self.font = os.path.join(path, self.font_name)
            self.name = config.get('name')
            self.version = config.get('version')
            self.font_layout = config.get('font_layout')
            self.font_type = config.get('font_type')

    def save_config(self):
        pass

    def setup_config_default(self):
        if gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path2 = os.path.join(path, 'gEngine', 'config.toml')
        if not os.path.exists(path2):
            default_config = ("[engine_config] \n"
                             "screen_width = 80 \n" 
                             "screen_height = 55 \n" 
                             "font = 'terminal10x10_gs_tc.png'")

            with open(os.path.join(path, 'gEngine', 'config.toml'), 'w') as f:
                f.write(default_config)
                f.close()
