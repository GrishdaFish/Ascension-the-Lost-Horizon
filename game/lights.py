import tcod as libtcod
import time


class LightHandler:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.lights = []
        self.tick_speed = 2

    def add_turn(self, ticker):
        ticker.schedule_turn(self.tick_speed, self)

    def add_light(self, light):
        self.lights.append(light)

    def remove(self, light):
        self.lights.remove(light)

    def update(self):
        for light in self.lights:
            light.update()
        for light in range(len(self.lights) - 1, 0, -1):
            if self.lights[light].dead:
                self.lights.pop(light)

    def render(self):
        for light in self.lights:
            self.gEngine.lightmask_add_light(light.x, light.y, light.color)


class Light:
    def __init__(self, x, y, handler, duration=0.0, decay=0.0, intensity=1.0, color=libtcod.light_yellow, flicker=False,
                 flicker_intensity=0.025):
        self.x = x
        self.y = y
        self.handler = handler
        self.duration = duration
        self.decay = decay
        self.intensity = intensity
        r = color[0]/255 * intensity
        g = color[1]/255 * intensity
        b = color[2]/255 * intensity
        self.original_color = color
        self.color = (r, g, b)
        self.flicker = flicker
        self.flicker_intensity = flicker_intensity
        self.time_now = None
        self.time_end = None
        if duration > 0:
            self.time_now = time.time()
            self.time_end = self.time_now + self.duration
        self.handler.add_light(self)
        self.dead = False
        self.randomize_color = False
        self.lerp_speed = 0
        self.lerp_interval = 0
        self.secondary_color = None
        self.reverse = False
        self.staged = False
        self.ramped = False

    def update(self):
        self.compute()
        if self.time_now:
            if self.time_now > self.time_end:
                # flag remove from light mask if duration is over
                self.dead = True
                return
        if self.intensity <= 0:  # flag remove if light is dead
            self.dead = True
            return

        # self.handler.add_light(self)
        return

    def compute(self):
        if self.time_now:
            self.time_now += (time.time() - self.time_now)
        if self.decay > 0:
            self.intensity -= self.decay
        if self.flicker:
            r = libtcod.random_get_float(0, -self.flicker_intensity, self.flicker_intensity)
            self.intensity += r
        if self.randomize_color:
            self.lerp_colors()
        elif self.staged:
            self.staged_lerp_compute()
        elif self.ramped:
            self.ramped_compute()
        else:
            r = self.original_color[0] / 255 * self.intensity
            g = self.original_color[1] / 255 * self.intensity
            b = self.original_color[2] / 255 * self.intensity
            self.color = (r, g, b)

    def staged_lerp(self, initial_intensity, target_intensity, initial_decay, final_decay, colors):
        """
        :param initial_intensity: How bright the initial burst of colors[0] is
        :param target_intensity: How bright the light is after the initial burst
        :param initial_decay: How fast the initial burst fades to target_intensity
        :param final_decay: How fast the light decays after target_intensity is hit
        :param colors: List of colors to be used. colors[0] is initial burst, colors[1] is target, then transition between
        :return: Nothing
        """
        self.staged = True
        self.initial_intensity = initial_intensity
        self.saved_intensity = initial_intensity
        self.intensity = target_intensity
        self.initial_decay = initial_decay
        self.decay = final_decay
        self.burst_colors = colors

    def staged_lerp_compute(self): #  2 colors for now
        if self.initial_intensity > self.intensity:
            col1 = self.burst_colors[0]
            col2 = self.burst_colors[1]
            decrease = self.saved_intensity - self.initial_intensity
            lerp_value = (decrease / self.saved_intensity)
            r, g, b = libtcod.color_lerp(col2, col1, 1.0 - lerp_value)
            r = r / 255 * self.initial_intensity
            g = g / 255 * self.initial_intensity
            b = b / 255 * self.initial_intensity
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
            self.initial_intensity -= self.initial_decay
            self.color = (r, g, b)
        else: # todo lerp through remaining burst_colors equally
            r, g, b = self.burst_colors[1]
            r = r / 255 * self.intensity
            g = g / 255 * self.intensity
            b = b / 255 * self.intensity
            #self.intensity -= self.final_decay
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
            self.color = (r, g, b)

    def lerp_colors(self):
        r = min(255, int(self.secondary_color[0] * 255))
        g = min(255, int(self.secondary_color[1] * 255))
        b = min(255, int(self.secondary_color[2] * 255))
        col2 = (r, g, b)
        color = libtcod.color_lerp(self.original_color, col2, self.lerp_speed)
        r = color[0] / 255 * self.intensity
        g = color[1] / 255 * self.intensity
        b = color[2] / 255 * self.intensity
        self.color = (r, g, b)
        if not self.reverse:
            self.lerp_speed += self.lerp_interval
        else:
            self.lerp_speed -= self.lerp_interval
        if self.lerp_speed >= 1.0 or self.lerp_speed <= 0.0:
            self.reverse = not self.reverse
            self.original_color = self.random_color()

    def randomize(self, speed=0.05):
        self.randomize_color = True
        self.lerp_speed = speed
        self.lerp_interval = speed
        self.secondary_color = self.random_color(True)

    def random_color(self, intensity=None):
        r = libtcod.random_get_int(0, 1, 255)
        g = libtcod.random_get_int(0, 1, 255)
        b = libtcod.random_get_int(0, 1, 255)
        if intensity:
            r = r / 255 * self.intensity
            g = g / 255 * self.intensity
            b = b / 255 * self.intensity
        return (r, g, b)

    def ramped_light(self, initial, target, ramp_speed, smooth_ramp=True):
        self.initial_intensity = initial
        self.target_intensity = target
        self.ramped = True
        self.ramp_speed = ramp_speed
        self.smooth_ramp = smooth_ramp

    def ramped_compute(self):
        if self.initial_intensity < self.target_intensity:
            if self.smooth_ramp:
                i = self.initial_intensity + self.decay + self.ramp_speed
            else:
                i = self.initial_intensity + self.decay + self.ramp_speed
                self.ramp_speed = self.ramp_speed + (self.ramp_speed * self.ramp_speed)

            self.initial_intensity = i
            self.intensity = i
            r, g, b = self.original_color
            r = r / 255 * self.intensity
            g = g / 255 * self.intensity
            b = b / 255 * self.intensity
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
            self.color = (r, g, b)
        else:
            self.intensity = self.target_intensity
            self.ramped = False