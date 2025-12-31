from components.component import Component
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty

class Image(Component, EventDispatcher):
    """
    Represents the image state - either frozen, blank, or neither.
    """
    frozen = BooleanProperty(False)
    blanked = BooleanProperty(False)

    def __init__(self):
        """
        Set initial state with freeze and blank disabled.
        """
        super().__init__()

        
    def set_freeze(self):
        """
        Send freeze command and update internal state.
        """
        self.commander.send_command("enable_freeze")
        self.frozen = True
        self.set_clock()

    def unset_freeze(self):
        """
        Send unfreeze command and update internal state.
        """
        self.commander.send_command("disable_freeze")
        self.frozen = False
        self.set_clock()

    def set_blank(self):
        """
        Send blank command and update internal state.
        """
        self.commander.send_command("disable_video")
        self.blanked = True
        self.set_clock()

    def unset_blank(self):
        """
        Send unblank command and update internal state.
        """
        self.commander.send_command("enable_video")
        self.blanked = False
        self.set_clock()
    
    def get_blank(self):
        """
        Return blank status boolean - true "blanked", false "unblanked"
        """
        return self.blanked
    
    def get_freeze(self):
        """
        Return freeze status boolean - true "frozen", flase "unfrozen"
        """
        return self.frozen
    
    def get_state(self):
        """
        Return image state in the form of tuple
        (bool freeze_state, bool blank_state, float duration).
        """
        freeze_state = self.get_freeze()
        blank_state = self.get_blank()
        duration = self.get_clock()
        return (freeze_state, blank_state, duration)