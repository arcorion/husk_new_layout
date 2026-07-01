import logging

from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.event import EventDispatcher
#from kivy.graphics import *
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from pathlib import Path
from random import choice
from time import sleep
import platform, threading

from components.logger import get_logger
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
        assert self.app is not None
    
    def select_input(self, input_name):
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
        main_screen = app.manager.get_screen('main')
        if (self.state == 'down'):
            app.sound.set_mute()
            main_screen.ids.audio_label.opacity = UNSELECTED_OPACITY
            main_screen.ids.volume.opacity = UNSELECTED_OPACITY
        else:
            app.sound.unset_mute()
            main_screen.ids.audio_label.opacity = SELECTED_OPACITY
            main_screen.ids.volume.opacity = SELECTED_OPACITY


class PowerButton(HuskyButton):
    """
    Describes the default settings for buttons in Huskontroller.
    """
    def __init__(self, **kwargs):
        super(PowerButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        assert self.app is not None
        self.allow_no_selection = False

    def call_unset_blank(self, timer):
        self.app.image.unset_blank()

    def call_unset_freeze(self, timer):
        self.app.image.unset_freeze()


class PowerOnButton(PowerButton):
    def __init__(self, **kwargs):
        super(PowerOnButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        assert self.app is not None

    def start_projector(self):
        self.app.start_projector()


class PowerOffButton(PowerButton):
    def __init__(self, **kwargs):
        super(PowerOffButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        assert self.app is not None

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

class TestModeGesture:
    """
    Tracks the secret tap sequence used to enter test mode:
    Display, Input, Audio, Input, Display labels, then a tap
    on the open background (Dubs) to the right of the controls.

    Resets to the start if a step arrives out of order, or if
    too much time passes between taps.
    """
    TIMEOUT = 3.0  # seconds allowed between taps before resetting

    def __init__(self, on_complete):
        self.sequence = ['display', 'input', 'audio', 'input', 'display', 'dubs']
        self.on_complete = on_complete
        self._index = 0
        self._timeout_event = None

    def register(self, step):
        expected = self.sequence[self._index]

        if step == expected:
            self._index += 1
            self._bump_timeout()
            if self._index == len(self.sequence):
                self._complete()
        else:
            # A fumbled attempt can restart immediately if the
            # mismatched tap happens to equal the first step.
            self._index = 1 if step == self.sequence[0] else 0
            if self._index:
                self._bump_timeout()
            else:
                self._cancel_timeout()

    def reset(self):
        self._index = 0
        self._cancel_timeout()

    def _complete(self):
        self.reset()
        self.on_complete()

    def _bump_timeout(self):
        self._cancel_timeout()
        self._timeout_event = Clock.schedule_once(lambda dt: self.reset(), self.TIMEOUT)

    def _cancel_timeout(self):
        if self._timeout_event:
            self._timeout_event.cancel()
            self._timeout_event = None


class KivyLogHandler(logging.Handler):
    """
    Pushes formatted log records into the running App's log_lines
    buffer, for the test-mode log pane. Records can arrive from any
    thread (e.g. the device monitor), so the actual buffer mutation
    is deferred to the Kivy thread via Clock.
    """
    MAX_LINES = 200

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(source)s] %(message)s",
            datefmt="%H:%M:%S"
        ))
        # Mirrors components/logger.py's SourceFilter - guarantees
        # %(source)s exists even if this handler somehow runs before
        # the file/console handlers have supplied a default.
        self.addFilter(self._default_source)

    @staticmethod
    def _default_source(record):
        if not hasattr(record, "source"):
            record.source = "system"
        return True

    def emit(self, record):
        message = self.format(record)
        Clock.schedule_once(lambda dt: self._append(message))

    def _append(self, message):
        lines = self.app.log_lines
        lines.append(message)
        if len(lines) > self.MAX_LINES:
            del lines[:len(lines) - self.MAX_LINES]


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        handled = super().on_touch_down(touch)
        app = App.get_running_app()

        if not handled and touch.x > self.ids.controls_box.right:
            app.gesture.register('dubs')
            return True

        gesture_labels = (
            self.ids.display_label,
            self.ids.input_label,
            self.ids.audio_label,
        )
        if not any(label.collide_point(*touch.pos) for label in gesture_labels):
            app.gesture.reset()

        return handled

class TestScreen(Screen):
    def __init__(self, **kwargs):
        super(TestScreen, self).__init__(**kwargs)

    def exit_test_mode(self):
        """
        Returns to the main interface. Resets the gesture tracker so
        a half-finished sequence from before entering test mode can't
        carry over and immediately re-trigger it.
        """
        app = App.get_running_app()
        app.gesture.reset()
        app.manager.current = 'main'


class HuskontrollerApp(App):
    # Capped rolling buffer of formatted log lines, fed by
    # KivyLogHandler, displayed in the test-mode log pane.
    log_lines = ListProperty([])

    def __init__(self, components_dictionary):
        super(HuskontrollerApp, self).__init__()
        self.image = components_dictionary["image"]
        self.input = components_dictionary["input"]
        self.projector = components_dictionary["projector"]
        self.sound = components_dictionary["sound"]
        self.controller = components_dictionary["controller"]
        self.controller.set_initial_state()
        self.manager = ScreenManager()
        self.gesture = TestModeGesture(
            on_complete=lambda: setattr(self.manager, 'current', 'test')
        )
        get_logger().addHandler(KivyLogHandler(self))

    def build(self):
        Builder.load_file("gui.kv")
        manager = self.manager
        manager.add_widget(MainScreen(name='main'))
        manager.add_widget(TestScreen(name='test'))

        return manager
    
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
