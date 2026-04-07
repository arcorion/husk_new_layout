# Huskontroller2
This is just [Huskontroller2](https://github.com/arcorion/huskontroller2/tree/main) with the GUI changed. I probably should've just forked this until I was done instead of making a new repo, but I was rushed and didn't think of that.

Huskontroller is a utility which provides a user interface for the AV systems used with the UW Communications classrooms. This is the second major version of the controller, written to improve expandability and correct some design flaws in the original version. The software assumes the hardware configuration we use in our classrooms.

## Touch Control Hardware
The following components are necessary to build the touch controls:
- Raspberry Pi 4
- Raspberry Pi Power Adapter
- 32GB microSD Card
- Pi Aluminum Heatsinks
- Official Raspberry Pi 7" Touch Display
- A USB to DB9 Serial adapter
- SmartiPi Touch Pro Case (Large)

The software as-is is designed to work with an Extron 1804 DO Switcher and most Panasonic projectors. (It will likely work with most Extron switchers, but I've only used it with this one model.) Different hardware can be used by replacing the "extron_serial.py" module with another module offering the same functions.

## Requirements to run the software
- Python 3.13 (older will work back to at least 3.9 - 3.14 breaks Kivy as I write this)
- pyserial 3.5
- Kivy 2.3.0

I know Kivy 2.3.1 works, but I haven't tested earlier or later than that. I think the requirements.txt pulls Kivy 2.3.1 since it's newer.

Python can be installed from Python.org or via your distro's repo. I've been using the repo on Raspberry Pi OS.
pyserial can be installed with pip on a dev machine:
`pip install pyserial`

In Pi OS, I believe it's installed by default. If not, you'll need to install from repo:
`sudo apt install python3-serial`

This is similar with Kivy:
`pip install kivy[base]`

And on Pi OS:
`sudo apt install python3-kivy`

The actual script is started with:
`python3 huskontroller.py`

If you try to start it without having the necessary serial ports attached and configured, it may raise an error that it can't find the serial port. There is a test device called "test_serial.py" which may be used if needed for testing. I've updated the code so that it should fall back to the test device in the most likely exception cases. In which case, it will just output the commands sent to the console.

## Sources used

Primary sources used for this are the documentation of the included modules.

- [PySerial](https://pyserial.readthedocs.io/en/latest/shortintro.html)
- [PSL's select module](https://docs.python.org/3/library/select.html)

I'm also using this to review Classes in Python.

- [Python 3.13.3 - Classes](https://docs.python.org/3/tutorial/classes.html)
