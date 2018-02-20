import numpy as np
import logging
# LEVEL=logging.DEBUG
LEVEL=logging.INFO
# HEIGHT=800
# WIDTH=1280
HEIGHT=480
WIDTH=640
EXPOSURE=-100

UPPER_BLUE = np.array([120,255,255])
LOWER_BLUE = np.array([15,100,100])

UPPER_CUBE = np.array([40,180,180])
LOWER_CUBE = np.array([20,120,100])

H = [0, 180.0]
S = [255, 255]
V = [35, 180]



# OTHER STUFF
	# brightness (int)    : min=30 max=255 step=1 default=-8193 value=50
	# contrast (int)    : min=0 max=10 step=1 default=57343 value=5
	# saturation (int)    : min=0 max=200 step=1 default=57343 value=83
	# white_balance_temperature_auto (bool)   : default=1 value=1
	# power_line_frequency (menu)   : min=0 max=2 default=2 value=2
	# 0: Disabled
	# 1: 50 Hz
	# 2: 60 Hz
	# white_balance_temperature (int)    : min=2800 max=10000 step=1 default=57343 value=4500 flags=inactive
	# sharpness (int)    : min=0 max=50 step=1 default=57343 value=25
	# backlight_compensation (int)    : min=0 max=10 step=1 default=57343 value=0
	# exposure_auto (menu)   : min=0 max=3 default=0 value=3
	# 1: Manual Mode
	# 3: Aperture Priority Mode
	# exposure_absolute (int)    : min=5 max=20000 step=1 default=156 value=6 flags=inactive
	# pan_absolute (int)    : min=-201600 max=201600 step=3600 default=0 value=0
	# tilt_absolute (int)    : min=-201600 max=201600 step=3600 default=0 value=0
	# zoom_absolute (int)    : min=0 max=10 step=1 default=57343 value=0