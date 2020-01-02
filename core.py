__author__ = 'GrishdaFish'
import gEngine.gEngine as gngine
import os
import sys
from game import main_menu
from game import splash_screen
from game import content_parser
import cProfile
import io
import pstats
import warnings



if __name__ == "__main__":
    # profiler = cProfile.Profile()
    # profiler.enable()

    #warnings.simplefilter('default')
    gEngine = gngine.gEngine()

    gEngine.init_root()
    gEngine.log_open_block("Starting up game")
    #main_menu = main_menu.MainMenu(gEngine)
    splash = splash_screen.SplashScreen(gEngine)
    gEngine.add_module(splash)

    gEngine.run()
    '''profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.dump_stats("logs/profiling/profile.dump")
    #convert profiling to human readable format
    import datetime
    date_and_time = datetime.datetime.utcnow()

    out_stream = open("logs/profiling/" + date_and_time.strftime("%y%m%d@%H%M") + ".profile", "w")
    ps = pstats.Stats("logs/profiling/profile.dump", stream=out_stream)
    ps.strip_dirs().sort_stats("cumulative").print_stats()'''