from components.component import Component
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty

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
        self.set_clock()

    def enable(self):
        """
        Command function, sets projector to on and sends command.
        """
        self.set_state("on")
        self.commander.send_command("enable_projector")
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
                self.power_state = True
            case "off":
                self.power_state = False
            case _:
                print("Error changing projector power state in Projector module.")