import time
from components.commander import Commander

"""
This module contains the Component class, which is the base class used
for each of the individual components. It provides a Clock object and a
Logger object for each component, so that they each can manage the last
state change and write to the Huskontroller log, respectively.
"""
class Component:
    """
    The Component class has the shared methods for implementing a given
    component. 
    
    The Component object will interact with the controller by passing
    along commands requested of it and by updating the controller with any
    pertinent changes to its state.
    """
    def __init__(self, name="Component", controller=None, enabled=False):
        """
        Initialize component with a string name, a controller controller, and
        a boolean enabled.
        """
        self.controller = controller
        self.name = name
        self.enabled = enabled
        self.clock = Clock()
        self.commander = Commander()

    def __repr__(self):
        return f"{self.get_state()}"

    def get_controller(self):
        """
        Return the controller object bound
        with this component.
        """
        return self.controller
    
    def set_controller(self, controller):
        """
        Takes controller object.
        Change the controller bound with this component.
        """
        self.controller = controller

    def set_clock(self):
        """
        Sets the clock's last timer to the current time
        """
        self.clock.set_clock()

    def get_clock(self):
        """
        Returns the duration since the last time the clock
        was set.
        """
        return self.clock.get_duration()
    
    def get_state(self):
        pass


class Clock:
    """
    Clock represents the duration since the last state change
    of a component. It stores the last time a state was changed
    and gets the duration since that last time.
    """
    def __init__(self):
        """
        Initialize clock with time at creation
        of clock.
        """
        self.last_state_change = time.time()
    
    def __repr__(self):
        """
        Returns a string of the duration float.
        """
        return f'{self.get_duration()}'

    def set_clock(self):
        """
        Update the clock to reflect the time
        of the last state change.
        """
        self.last_state_change = time.time()

    def get_duration(self):
        """
        Return float (in seconds) representing the duration passed
        since the last state change.
        """
        duration = time.time() - self.last_state_change
        return duration