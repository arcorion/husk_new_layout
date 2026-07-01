from components.component import Component
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from time import sleep


class Projector(Component, EventDispatcher):
    """
    Represents the projector's state - either "off" or "on",
    as well as how long it has been since its state was
    last changed.
    """
    power_state = BooleanProperty(False)

    def __init__(self):
        """
        Initialize projector object, setting power state to off
        by default and initializing clock.
        """
        super().__init__()

    def disable(self):
        """
        Command function, sets projector to off and sends command.
        """
        self.set_state("off")
        self.commander.send_command("disable_projector")
        sleep(0.5)
        self.commander.send_command("disable_projector")
        sleep(0.5)
        self.commander.send_command("disable_projector")        
        self.set_clock()

    def enable(self):
        """
        Command function, sets projector to on and sends command.
        """
        self.set_state("on")
        self.commander.send_command("enable_projector")
        sleep(0.5)
        self.commander.send_command("enable_projector")
        sleep(0.5)
        self.commander.send_command("enable_projector")
        self.set_clock()

    def test_enable(self):
        """
        Test-mode variant of enable(). Sends the raw command once,
        with no retries and no delay - for bench-testing the
        projector's response directly. Still updates power_state,
        same as the real button.
        """
        self.set_state("on")
        self.commander.send_command("enable_projector")
        self.set_clock()

    def test_disable(self):
        """
        Test-mode variant of disable(). Sends the raw command once,
        with no retries and no delay. Still updates power_state,
        same as the real button.
        """
        self.set_state("off")
        self.commander.send_command("disable_projector")
        self.set_clock()

    def get_power_state(self):
        """
        Return the power state string "off" or "on".
        """
        return self.power_state

    def get_state(self):
        """
        Return the projector state in the form
        (string power_state, float duration)
        """
        power_state = self.get_power_state()
        duration = self.get_clock()
        return (power_state, duration)

    def set_state(self, state):
        """
        Take a string representing the state. "on" turns power on, "off" turns
        it off.
        """
        match state:
            case "on":
                Clock.schedule_once(lambda dt: setattr(self, 'power_state', True))
            case "off":
                Clock.schedule_once(lambda dt: setattr(self, 'power_state', False))
            case _:
                self.commander.log.error("Error changing projector power state in Projector module.")