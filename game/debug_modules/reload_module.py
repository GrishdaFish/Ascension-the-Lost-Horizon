__author__ = 'GrishdaFish'
import importlib
import imp
import textwrap
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import popups
from gEngine import particle
from game.spells import spells
from game.spells import spell_effects


class ReloadModule(window_widget.WindowWidget):
    def setup(self):
        self.alert_x = self.gEngine.w / 4
        self.alert_y = self.gEngine.h / 4

        self.buttons = []
        button = button_widget.TextButtonWidget(self, 1, 1, "Particles", self.reload_particles)
        self.buttons.append(button)

        button = button_widget.TextButtonWidget(self, 1, 2, "Spells", self.reload_spells)
        self.buttons.append(button)

        button = button_widget.TextButtonWidget(self, 1, 3, "Spell Effects", self.reload_spell_effects)
        self.buttons.append(button)

    def update(self, key, mouse):
        try:
            for button in self.buttons:
                button.run(key, mouse)

        except BaseException as e:
            if str(e) != "None":
                self.send_alert(str(e), "Error!")

    def send_alert(self, msg, title):
        alert = popups.Alert(self.gEngine, x=self.alert_x, y=self.alert_y, w=len(msg), title=title)
        alert.setup(msg)
        alert.activate()
        self.gEngine.bring_module_to_front(alert)

    def reload_particles(self):
        game = self.gEngine.get_module_by_name("Game")
        self.gEngine.particle_clear()
        imp.reload(particle)
        if game:
            game.build_objects.reload_content()
        msg = "Particle Module Reloaded"
        self.send_alert(msg, "Reloaded")


    def reload_spells(self):
        imp.reload(spells)
        game = self.gEngine.get_module_by_name("Game")
        if game:
            game.build_objects.reload_content()
        msg = "Spells Module Reloaded"
        self.send_alert(msg, "Reloaded")

    def reload_spell_effects(self):
        imp.reload(spell_effects)
        game = self.gEngine.get_module_by_name("Game")
        if game:
            game.build_objects.reload_content()
        msg = "Spell Effects Module Reloaded"
        self.send_alert(msg, "Reloaded")