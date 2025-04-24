__author__ = 'GrishdaFish'
import gEngine.gEngine as gngine
from game import main_menu



if __name__ == "__main__":
    gEngine = gngine.gEngine()

    gEngine.init_root()
    gEngine.log_open_block("Starting up game")
    main_menu = main_menu.MainMenu(gEngine)
    gEngine.add_module(main_menu)

    gEngine.run()