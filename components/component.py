# import logging
# import os
# from pathlib import Path

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
        # Enable log
        # To disable, set True to False.
        # self.log = Logger(self._name, True)

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
        self._last_state_change = time.time()

    def get_duration(self):
        """
        Return float (in seconds) representing the duration passed
        since the last state change.
        """
        duration = time.time() - self.last_state_change
        return duration

'''
class Logger:
    """
    Logger object that gets used to write to the log file.
    """
    _logger = logging.getLogger('huskontroller')
    _logger.setLevel(logging.DEBUG)

    # Set the log path to the application_root/logs folder.
    _log_path = Path.cwd()
    _log_path = _log_path.parent
    _log_path = _log_path / 'logs'

    # Make sure the log directory exists
    if not _log_path.exists():
        _log_path.mkdir()

    # Assign the main and backup log paths
    _main_log = _log_path / 'huskontroller.log'
    _backup_log = _log_path / 'backup.log'

    # Set maximum log size to 100MB, copy main to backup,
    # and delete the log file, if overly large.
    _logger_size_limit = 100 * 1024 * 1024
    if _main_log.exists():
        _log_size = os.path.getsize(_main_log)
        if _log_size > _logger_size_limit:
            if _backup_log.exists():
                os.remove(_backup_log)
            os.rename(_main_log, _backup_log)

    # Set the filehandler output to huskontroller.log
    _file_handler = logging.FileHandler(_main_log)
    _file_handler.setLevel(logging.DEBUG)

    # Using the format "YYYY-MM-DD HH:MM:SS" for the timestamp, then a
    # dash, and then the actual message.
    _formatter = logging.Formatter(fmt='%(asctime)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    _file_handler.setFormatter(_formatter)

    # Appl
    _logger.addHandler(_file_handler)

    def __init__(self, instance_name, enabled=False):
        """
        Takes a string instance_name and boolean enabled.
        The instance name field adds itself immediately after
        each log line's time and before the actual log contents.

        The enabled boolean does what it says. It enables or disables
        logging to disk.
        """
        self._instance_name = instance_name
        self._logger.info(f'Enabling logging for {self._instance_name}')
        self.enabled = enabled
    
    def info(self, log_string):
        """
        Writes the string "log_string" to the log file as an info log.
        """
        if self.enabled:
            self._logger.info(f"{self._instance_name}: {log_string}")

    def warning(self, log_string):
        """
        Writes the string "log_string" to the log file as a warning log.
        """
        if self.enabled:
            self._logger.warning(f"{self._instance_name}: {log_string}")
    
    def error(self, log_string):
        """
        Writes the string "log_string" to the log file as an error log.
        """
        if self.enabled:
            self._logger.error(f"{self._instance_name}: {log_string}")
            
'''