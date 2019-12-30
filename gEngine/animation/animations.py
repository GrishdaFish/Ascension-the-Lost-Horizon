__author__ = 'GrishdaFish'
from gEngine import gEngine as _gEngine
import tcod as libtcod
import sys
import os
import distutils.util as dist_util

class Animation:
    def __init__(self, animation, loop, hold_last_frame, name):
        """
        A container class for animations
        :param animation: a list of frames for the animation
        :param loop: Does this animation loop?
        :param hold_last_frame: Should this animation hold on its last frame?
        :param name: The name of the directory the animation was contained in
        """
        self.animation = animation
        self.loop = loop
        self.hold_last_frame = hold_last_frame
        self.name = name


class Animations:
    def __init__(self, gEngine):
        """
        An animation system for the Horizon Engine
        :param gEngine:
        """
        self.animations = []
        self.gEngine = gEngine

    def load_animations(self):
        """
        Loads all animations from the content/img/animations directory
        Animations should be numbered and png, eg 0.png - 49.png
        :return:
        """
        self.gEngine.log_open_block("Loading all animation files")
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        root_path = os.path.join(path, 'content', 'img', 'animations')
        root_directories = os.listdir(root_path)
        for dir in root_directories:
            sub_dir = os.listdir((os.path.join(root_path, dir)))
            # if the directory doesnt have a controller in it, its either not an end directory, or an invalid animation
            if "controller.dat" in sub_dir:
                # First, load the animation controller
                controller = open(os.path.join(root_path, dir, "controller.dat")).readlines()
                loop = controller[4]
                loop = bool(dist_util.strtobool(loop.strip().lower()))
                hold = controller[7]
                hold = bool(dist_util.strtobool(hold.strip().lower()))
                # then we load all of the animation files into an array
                animation = []
                png_holder = []
                for file in sub_dir:
                    # first we check all of the files to make sure they are .png
                    if os.path.splitext(os.path.join(root_path, dir, file))[1] == '.png':
                        # then we append them all to a temporary list for sorting
                        # we remove the extension for sorting numerically to preserve animation ordering
                        png_holder.append(file.strip('.png'))
                # sort the list numerically to preserve animation order
                png_holder.sort(key=int)
                for img in png_holder:
                    animation.append(self.gEngine.image_load(os.path.join(root_path, dir, img, '.png')))
        self.gEngine.log_message("Animations loaded.")
        self.gEngine.log_close_block()


    def get_animation(self, name):
        return self.animations[name]

    def draw_animation(self):
        pass

