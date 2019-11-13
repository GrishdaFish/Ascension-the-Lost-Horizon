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
            #else:
            #    l = self.lights[light]
            #    self.gEngine.lightmask_add_light(l.x, l.y, l.color)

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
        r = self.original_color[0] / 255 * self.intensity
        g = self.original_color[1] / 255 * self.intensity
        b = self.original_color[2] / 255 * self.intensity
        self.color = (r, g, b)

