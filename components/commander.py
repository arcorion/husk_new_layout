import serial
from serial.tools import list_ports

class Commander:
    """
    Commander handles the command string that is
    sent to the Extron device.

    It associates the commands themselves with a useful
    name for easy use in other methods.
    """
    def __init__(self):
        self.command_list = {
            'select_podium': '1!',
            'select_hdmi': '2!',
            'select_usbc': '3!',
            'select_vga': '4!',
            'view_current_input': '!',
            'enable_freeze': '1*1F',
            'disable_freeze': '1*0F',
            'get_freeze_status': '1F',
            'disable_video': '1*1B',
            'enable_video': '1*0B',
            'get_video_status': '1*B',
            'enable_projector': 'W+snds9*9|%02PON%03',
            'disable_projector': 'W+snds9*9|%02POF%03',
            'get_volume': 'V',
            'disable_audio': '1Z',
            'enable_audio': '0Z',
            'get_audio_status': 'Z'
        }

        try:
            port_list = list_ports.comports()
            port_names = []
            for port in port_list:
                port_names += port
            self._device = serial.Serial(port_names[0], 9600)
            print(f'Device {self._device} created.')
        except serial.SerialException:
            print(f'Error opening connection to port: {port_list[0]}')
            self._device = TestSerial()


    def send_command(self, command, custom=False):
        """
        Takes a command string and sends the command as an
        encoded byte string to the Extron device.
        """
        command_string = self.command_list.get(command)
        if command_string:
            self._device.write(command_string.encode())
            print(f'Command sent: {command_string}')
        elif custom == True:
            self._device.write(command.encode())
            print(f'Custom command sent: {command}')
        else:
            print(f'Unsupported command: {command}')

class TestSerial:

    def write(self, command):
        output = 'Serial Out: ' + command.decode()