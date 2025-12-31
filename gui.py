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

class DefaultButton(ToggleButton):
    """
    Describes the default settings for buttons in Huskontroller.
    """
    def __init__(self, **kwargs):
        super(DefaultButton, self).__init__(**kwargs)



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


if __name__ == '__main__':
    HuskontrollerApp().run()
