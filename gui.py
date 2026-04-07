from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.graphics import *
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from pathlib import Path
from random import choice
from time import sleep
import platform, threading

from components.sound import Sound

UNSELECTED_OPACITY = 0.7
SELECTED_OPACITY = 1.0
INPUT_DISPLAY_NAMES = {
    "podium": "Podium",
    "hdmi": "HDMI",
    "usbc": "USB-C",
    "vga": "VGA"
}

operating_system = platform.system()
match operating_system:
    case 'Linux':
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', '480')
        Window.show_cursor = False
    case 'Windows' | 'Darwin':
        Window.size = (800, 480)
    case _:
        Exception("Not a supported OS")


class HuskyButton(ToggleButton):
    def __init__(self, **kwargs):
        super(HuskyButton, self).__init__(**kwargs)
        self.opacity = UNSELECTED_OPACITY

    def on_state(self, *args):
        if self.state == 'normal':
            self.opacity = UNSELECTED_OPACITY
        else:
            self.opacity = SELECTED_OPACITY

class InputButton(HuskyButton):
    def __init__(self, **kwargs):
        super(InputButton, self).__init__(**kwargs)
        self.allow_no_selection = False
        self.app = App.get_running_app()
    
    def select_input(self, input_name):
        if not self.app.projector.power_state:
            self.app.start_projector(input_name)
        else:
            getattr(self.app.controller, f'set_input_{input_name}')()


class MuteButton(ToggleButton):
    def __init__(self, **kwargs):
        super(MuteButton, self).__init__(**kwargs)

    def on_state(self, *args):
        if self.state == 'normal':
            self.opacity = SELECTED_OPACITY
        else:
            self.opacity = UNSELECTED_OPACITY
    
    def change_state(self, app):
        if (self.state == 'down'):
            app.sound.set_mute()
            app.root.ids.audio_label.opacity = UNSELECTED_OPACITY
            app.root.ids.volume.opacity = UNSELECTED_OPACITY
        else:
            app.sound.unset_mute()
            app.root.ids.audio_label.opacity = SELECTED_OPACITY
            app.root.ids.volume.opacity = SELECTED_OPACITY


class PowerButton(HuskyButton):
    """
    Describes the default settings for buttons in Huskontroller.
    """
    def __init__(self, **kwargs):
        super(PowerButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.allow_no_selection = False

    def call_unset_blank(self, timer):
        self.app.image.unset_blank()

    def call_unset_freeze(self, timer):
        self.app.image.unset_freeze()


class PowerOnButton(PowerButton):
    def __init__(self, **kwargs):
        super(PowerOnButton, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def start_projector(self):
        self.app.start_projector()


class PowerOffButton(PowerButton):
    def __init__(self, **kwargs):
        super(PowerOffButton, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def stop_projector(self):
        Clock.schedule_once(self.call_unset_blank, 1)
        Clock.schedule_once(self.call_unset_freeze, 1)
        threading.Thread(target=self.app.controller.turn_off_projector, daemon=True).start()
        power_off_message = PowerPopup("off")
        power_off_message.open()


class PowerPopup(Popup):
    def __init__(self, on_off_text="on", input_name=None, **kwargs):
        super(PowerPopup, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.auto_dismiss = False
        self.background = ''
        self.background_color = (232/255, 211/255, 162/255, 1)
        self.input_name = input_name
        self.on_off_text = on_off_text
        self.seconds = self.app.controller.PROJECTOR_WAIT
        self.separator_color = [50/255, 0/255, 110/255, 1]
        self.size_hint = (0.9, 0.9)
        self.title = 'Projector'
        self.title_align = 'center'
        self.title_color = [0, 0, 0, 1]
        self.title_font = './fonts/open_sans_regular.ttf'
        self.title_size = '36sp'
        
        if self.input_name:
            self.message = f"Powering {self.on_off_text}.\nSwitching to {INPUT_DISPLAY_NAMES.get(self.input_name)}.\nInterface available in {self.seconds} seconds."
        else:
            self.message = f"Powering {self.on_off_text}.\nInterface available in {self.seconds} seconds."
        self.content = Label(text=self.message, color=[0, 0, 0, 1], font_size='24sp', halign='center')

        Clock.schedule_interval(self.update_message, 1)

    def update_message(self, seconds):
        self.seconds -= 1
        if self.seconds == 0:
            self.dismiss()
        else:
            if self.input_name:
                self.content.text = f"Powering {self.on_off_text}.\nSwitching to {INPUT_DISPLAY_NAMES.get(self.input_name)}.\nInterface available in {self.seconds} seconds."
            else:
                self.content.text = f"Powering {self.on_off_text}.\nInterface available in {self.seconds} seconds."


class TouchPanel(FloatLayout):
    def __init__(self, **kwargs):
        super(TouchPanel, self).__init__(**kwargs)


class HuskontrollerApp(App):
    def __init__(self, components_dictionary):
        super(HuskontrollerApp, self).__init__()
        self.image = components_dictionary["image"]
        self.input = components_dictionary["input"]
        self.projector = components_dictionary["projector"]
        self.sound = components_dictionary["sound"]
        self.controller = components_dictionary["controller"]
        self.controller.set_initial_state()

    def build(self):
        Builder.load_file("gui.kv")
        return TouchPanel()
    
    def start_projector(self, input_name=None):
        """
        Start the projector components - this is called by
        power on and input switch buttons when the projector is off.
        """
        # Guards against starting the projector twice if a button
        # is pressed.
        if self.projector.power_state:
            return
        threading.Thread(target=self.controller.turn_on_projector, daemon=True).start()
        PowerPopup(input_name=input_name).open()
        Clock.schedule_once(lambda dt: self.image.unset_blank(), 10)
        Clock.schedule_once(lambda dt: self.image.unset_freeze(), 10)
        if input_name:
            Clock.schedule_once(lambda dt: getattr(self.controller, f'set_input_{input_name}')(), self.controller.PROJECTOR_WAIT)


if __name__ == '__main__':
    HuskontrollerApp().run()
