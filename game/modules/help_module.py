__author__ = 'noobspanker'
from gEngine.utilities.widget import window_widget, button_widget


class HelpModule(window_widget.WindowWidget):
    def close(self):
        # close all the shit
        self.exit_button.close()
        pass

    def setup(self):
        # define all the shit we want to show
        self.exit_label = "Back"
        self.exit_button = button_widget.ButtonWidget(self, len(self.exit_label)+2, 40, self.exit_label, self.close)
        self.alpha_disclaimer = "ALPHA VERSION! Be aware bugs may exist, you can help by reporting at criricalmiss-studios.com"
        pass

    def update(self, key, mouse):
        # show all the shit
        self.exit_button.run(key, mouse)
        pass