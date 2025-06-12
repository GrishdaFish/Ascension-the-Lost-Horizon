from configparser import SafeConfigParser
import sys
import os
import toml

path = os.path.abspath('.')
options = os.path.join(path, 'options.toml')
custom_font = os.path.join(path, 'custom_font.toml')

def load_options():
    f = open(options).read()
    parsed_options = toml.loads(f)
    for item in parsed_options:
        print(item)
    keys = parsed_options.get('keys')
    wasd = keys.get('wasd')
    print(wasd)
    
if __name__ == '__main__':
    load_options()

