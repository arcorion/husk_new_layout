import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from components.commander import Commander
from components.logger import get_logger

class DeviceMonitor:
    PING_COMMANDS = {
        'switcher': '1*I',  # Extron: returns general info (input type, mute status, frequencies)
    }

    def __init__(self, interval=30, on_ping=None):
        self.on_ping = on_ping
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None
        self.commander = Commander()
        self.log = get_logger()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.log.info("Device monitor started.", extra={"source": "monitor"})

    def stop(self):
        self._stop_event.set()
        self.log.info("Device monitor stopped.", extra={"source": "monitor"})

    def _loop(self):
        while not self._stop_event.wait(self.interval):
            # Commander() call triggers __init__ health check —
            # reconnects silently if port dropped since last cycle.
            self.commander = Commander()
            self._ping_all()

    def _ping_all(self):
        for device, raw_cmd in self.PING_COMMANDS.items():
            response = self.commander.send_and_read(raw_cmd, source=device)
            if response is None:
                self.log.info(f"{device} ping skipped (port busy or error)", extra={"source": "monitor"})
            else:
                self.log.info(f"{device} ping -> {response!r}", extra={"source": "monitor"})
                if self.on_ping:
                    self.on_ping(device, response)
