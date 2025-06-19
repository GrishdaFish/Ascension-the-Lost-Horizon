__author__ = 'GrishdaFish'
import os
import toml
import tcod as libtcod

class CellAnimation:
    def __init__(self, gEngine, con, frames=None, loop=False, x=0, y=0, color=libtcod.white, delay=0, fore=True):
        self.gEngine = gEngine
        self.con = con
        if frames is None:
            frames = []
        self.frames = frames
        self.loop = loop
        self.x = x
        self.y = y
        self.color = color
        self.index = 0
        self.max_delay = delay
        self.delay = 0
        self.finished = False
        self.fore = fore

    def draw(self, map=True):
        if self.delay > self.max_delay:
            self.index += 1
            self.delay = 0
        self.delay += 1
        char = self.get_frame()
        if map:
            if self.gEngine.map_is_in_fov(int(self.x), int(self.y)):
                col = self.gEngine.get_map_tile_color(int(self.x), int(self.y))
                br, bg, bb = col
                fr, fg, fb = self.color
                brightness = self.gEngine.lightmask_get_mask_value(self.x, self.y)
                fr *= brightness[0]
                fg *= brightness[1]
                fb *= brightness[2]
                br *= brightness[0]
                bg *= brightness[1]
                bb *= brightness[2]
                fr = int(min(255, fr))
                fg = int(min(255, fg))
                fb = int(min(255, fb))
                br = int(min(255, br))
                bg = int(min(255, bg))
                bb = int(min(255, bb))
                self.gEngine.console_put_char_ex(self.con, int(self.x), int(self.y), char, (fr, fg, fb), (br, bg, bb))
        else:
            br, bg, bb = libtcod.black
            fr, fg, fb = self.color
            self.gEngine.console_put_char_ex(self.con, int(self.x), int(self.y), char, (fr, fg, fb), (br, bg, bb))

    def get_frame(self):
        if self.index > len(self.frames)-1:
            self.index = 0
        return self.frames[self.index]

class Animation:
    def __init__(self, animation, loop, hold_last_frame, name, reverse):
        """
        A container class for animations
        :param animation: a list of frames for the animation
        :param loop: Does this animation loop?
        :param hold_last_frame: Should this animation hold on its last frame?
        :param name: The name of the directory the animation was contained in
        :param reverse: Should the animation loop backwards?
        """
        self.animation = animation
        self.loop = loop
        self.hold_last_frame = hold_last_frame
        self.name = name
        self.reverse = reverse
        self.index = 0
        self.length = len(self.animation) - 1
        self.finished = False

    def get_current_frame(self):
        if self.finished and not self.hold_last_frame:
            return None
        return self.animation[self.index]

    def update(self):
        if self.index < self.length:
            self.index += 1
        else:
            if self.reverse:
                self.index = 0
                self.animation.reverse()
                self.finished = True
            else:
                self.index = self.length
                self.finished = True
        return self.finished

    def reset(self):
        self.index = 0
        self.finished = False

class Animations:
    def __init__(self, gEngine):
        """
        An animation system for the Horizon Engine
        :param gEngine:
        """
        self.animations = []  # TODO Consider making this a dict
        self.cell_animations = []
        self.gEngine = gEngine

    def add_cell_animation(self, cell_animation):
        self.cell_animations.append(cell_animation)


    def load_animations(self, root_path=None):
        """
        Loads all animations from the content/img/animations directory
        Animations should be numbered and png, eg 0.png - 49.png
        :return:
        """
        self.gEngine.log_open_block("Loading all animation files")
        path = os.path.abspath('.')
        if not root_path:
            root_path = os.path.join(path, 'content', 'img', 'animations')
        for root, dirs, files in os.walk(root_path):
            if len(files) > 0:
                if "controller.toml" in files:
                    self.gEngine.log_open_block("Loading animations in %s" % root)
                    # First, load the animation controller
                    loop, freeze, name, reverse = self.parse_controller(os.path.join(root, "controller.toml"))
                    animation = []
                    png_holder = []
                    for file in files:
                        # first we check all of the files to make sure they are .png
                        if os.path.splitext(os.path.join(root, file))[1] == '.png':
                            # then we append them all to a temporary list for sorting
                            # we remove the extension for sorting numerically to preserve animation ordering
                            png_holder.append(file.strip('.png'))
                    # sort the list numerically to preserve animation order
                    png_holder.sort(key=int)
                    for img in png_holder:
                        animation.append(self.gEngine.image_load(os.path.join(root, img + '.png')))
                    self.animations.append(Animation(animation, loop, freeze, name, reverse))
                    self.gEngine.log_message("Loaded animations in %s" % root)
                    self.gEngine.log_close_block()

        self.gEngine.log_message("Animations loaded.")
        self.gEngine.log_close_block()

    def parse_controller(self, path):
        """
        Parses the controller toml
        :param path: path to the toml
        :return: all of the toml values
        """
        name = path.split('\\')
        name = name[len(name)-2]
        file = open(path).read()
        content = toml.loads(file)
        loop = content.get("loop")
        freeze = content.get("freeze")
        reverse = content.get('reverse')
        return loop, freeze, name, reverse

    def draw_animation(self, animation_name, target, x, y):
        """

        :param animation_name: The name of the animation to draw
        :param target: the console to draw to
        :param x: the x position of the upper left corner of the image to be blit on the target console
        :param y: the y position of the upper left corner
        :return:
        """
        for animation in self.animations:
            if animation.name == animation_name:
                img = animation.get_current_frame()
                if img:
                    self.gEngine.image_blit_2x(img, target, x, y)
                return animation.update()

    def draw_cell_animations_back(self, map):
        for animation in self.cell_animations:
            if not animation.fore:
                animation.draw(map)
                if animation.finished:
                    self.cell_animations.remove(animation)

    def draw_cell_animations_fore(self, map):
        for animation in self.cell_animations:
            if animation.fore:
                animation.draw(map)
                if animation.finished:
                    self.cell_animations.remove(animation)

    def reset_animation(self, animation_name):
        for animation in self.animations:
            if animation.name == animation_name:
                animation.reset()
                return

    def clear_cell_animations(self):
        self.cell_animations.clear()

    def remove_cell_animation(self, cell):
        self.cell_animations.remove(cell)