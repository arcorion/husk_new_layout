import serial
import threading
import time

from serial.tools import list_ports

class Commander:
    """
    Commander handles the command string that is
    sent to the Extron device.

    It associates the commands themselves with a useful
    name for easy use in other methods.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # This is new for me, so commenting - creating a new class instance
        # This creates a singleton.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
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
        self._initialized = True

        try:
            port_list = [p for p in list_ports.comports() if 'com0com' not in p.description.lower()]
            self._device = serial.Serial(port_list[0].device, 9600, timeout=2)
            print(f'Device {self._device} created.')
        except (serial.SerialException, IndexError):
            print(f'Error opening connection to serial port\nUsing test serial.')
            self._device = TestSerial()

    @property
    def connection_status(self):
        if isinstance(self._device, TestSerial):
            return "No serial device found — using TestSerial"
        else:
            return f"Connected: {self._device.port} @ {self._device.baudrate} baud"

    def read_response(self):
        """
        Reads one line from the serial device, returning it. If nothing
        received, times out and returns None.
        """
        try:
            return self._device.readline().decode().strip()
        except Exception:
            return None

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
    _STREAM_MESSAGES = [b'Inp1\n', b'Vol063\n', b'JustTesting1\n']
    _MESSAGE_SECONDS = 3

    def __init__(self):
        self._last_command = b'TestSerial Initialized'
        self._last_stream_time = time.time()
        self._stream_index = 0

    @property
    def in_waiting(self):
        return 1 if time.time() - self._last_stream_time >= self._MESSAGE_SECONDS else 0

    def readline(self):
        if time.time() - self._last_stream_time >= self._MESSAGE_SECONDS:
            self._last_stream_time = time.time()
            msg = self._STREAM_MESSAGES[self._stream_index % len(self._STREAM_MESSAGES)]
            self._stream_index += 1
            with open("debug.log", "a") as f:
                f.write(f"TestSerial stream: {msg}\n")
            return msg
        return b'Echo Last: ' + self._last_command
    
    def write(self, command):
        self._last_command = command
        print(command.decode())