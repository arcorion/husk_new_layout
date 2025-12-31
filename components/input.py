from components.component import Component
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty

class Input(Component, EventDispatcher):
    """
    The Input component manages the state of the AV
    input. It ensures that one of the four inputs,
    "podium", "hdmi", "usbc", and "vga" are selected
    and provides a getter module for the input.
    """

    INPUTS = ["podium", "hdmi", "usbc", "vga"]
    input = NumericProperty(0)

    def __init__(self, commander):
        super(Input, self).__init__()
        self.commander = commander
        
    def set_input(self, input):
        """
        Attempt to set the input based off a passed string.
        "podium", "hdmi", "usbc", and "vga" are allowed.

        If nothing matches, just uses podium as a default.
        """
        if input in self.INPUTS: 
            index = self.INPUTS.index(input)
        else:
            index = 0
        
        # Input number set from index
        self.input = index

        # Commander expects 1-4, not 0-3, so increment and then
        # append to select string.
        input_command = "select_" + str(self.INPUTS[self.input])

        self.commander.send_command(input_command)

    def set_hdmi(self):
        self.set_input("hdmi")

    def set_podium(self):
        self.set_input("podium")

    def set_usbc(self):
        self.set_input("usbc")

    def set_vga(self):
        self.set_input("vga")

    def get_input(self):
        """
        Return a string of the currently set input,
         Options: "podium", "hdmi", "usbc", or "vga"
        """
        return self.INPUTS[self.input]
    
    def get_state(self):
        """
        Return the state of the input as a tuple in the form
        (string input, float duration).
        """
        input = self.get_input()
        duration = self.get_clock()
        return (input, duration)