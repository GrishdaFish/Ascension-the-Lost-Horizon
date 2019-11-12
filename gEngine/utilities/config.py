import os
import sys
import toml

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
        with open(os.path.join(sys.path[0], 'gEngine', 'config.toml')) as config:
            config = config.read()
            config = toml.loads(config)
            config = config.get('engine_config')
            self.screen_width = config.get('screen_width')
            self.screen_height = config.get('screen_height')
            self.font_name = config.get('font')
            self.font = os.path.join(sys.path[0], self.font_name)
            self.name = config.get('name')
            self.version = config.get('version')
            self.font_layout = config.get('font_layout')
            self.font_type = config.get('font_type')

    def save_config(self):
        pass

    def setup_config_default(self):
        path = os.path.join(sys.path[0], 'gEngine', 'config.toml')
        if not os.path.exists(path):
            default_config = ("[engine_config] \n"
                             "screen_width = 80 \n" 
                             "screen_height = 55 \n" 
                             "font = 'terminal10x10_gs_tc.png'")

            with open(os.path.join(sys.path[0], 'gEngine', 'config.toml'), 'w') as f:
                f.write(default_config)
                f.close()
