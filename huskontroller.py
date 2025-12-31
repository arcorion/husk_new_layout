from time import sleep

from components.commander import Commander
from components.image import Image
from components.input import Input
from components.projector import Projector
from components.sound import Sound
from gui import HuskontrollerApp

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty

class Huskontroller(EventDispatcher):
    def __init__(self):
        self._commander = Commander()
        self.image = Image()
        self.input = Input(self._commander)
        self.projector = Projector()
        self.sound = Sound()

        # Defines wait time between projector start
        # and sending the first command
        self.PROJECTOR_WAIT = 20

        self.components_dictionary = {
            "image" : self.image,
            "input" : self.input,
            "projector" : self.projector,
            "sound" : self.sound,
            "controller" : self
        }
        
        self.touchscreen = HuskontrollerApp(self.components_dictionary)
        self.touchscreen.run()

    def set_initial_state(self):
        """
        Set default state of the AV system. Projector is turned off,
        Image is set to unfrozen and unblanked, Input is set to podium,
        sound is enabled and set to volume of 50.
        """
        self.image.unset_blank()
        self.image.unset_freeze()
        self.input.set_input("podium")
        self.sound.unset_mute()
        self.sound.set_volume(50)
        self.projector.disable()

    def turn_on_projector(self):
        self.projector.enable()
        sleep(self.PROJECTOR_WAIT)
        # These are moved to the GUI, as this function runs outside
        # of the main thread of Kivy and can't update Kivy components.
        # self.image.unset_blank()
        # self.image.unset_freeze()
    
    def turn_off_projector(self):
        # These are moved to the GUI, as this function runs outside
        # of the main thread of Kivy and can't update Kivy components.
        # self.image.unset_blank()
        # self.image.unset_freeze()
        sleep(self.PROJECTOR_WAIT/2)
        self.projector.disable()
    
    def set_input_podium(self):
        power_on = self.projector.get_power_state()
        if not power_on:
            self.turn_on_projector()
        self.input.set_input("podium")

    def set_input_hdmi(self):
        power_on = self._projector.get_power_state()
        if not power_on:
            self.turn_on_projector()
        self.input.set_input("hdmi")

    def set_input_usbc(self):
        power_on = self.projector.get_power_state()
        if not power_on:
            self.turn_on_projector()
        self.input.set_input("usbc")

    def set_input_vga(self):
        power_on = self.projector.get_power_state()
        if not power_on:
            self.turn_on_projector()
        self.input.set_input("vga")

    def turn_on_blank(self):
        self.image.set_blank()
    
    def turn_off_blank(self):
        self.image.unset_blank()

    def turn_on_freeze(self):
        self.image.set_freeze()

    def turn_off_freeze(self):
        self.image.unset_freeze()

    def toggle_camera(self):
        """
        Not implemented - will toggle camera off
        and on when done.
        """
        pass

    def set_volume(self, volume):
        self.sound.unset_mute()
        self.sound.set_volume(volume)
    
    def toggle_mute(self):
        muted = self.sound.get_mute()
        if muted:
            self.sound.unset_mute()
        else:
            self.sound.set_mute()

if __name__ == '__main__':
    controller = Huskontroller()
