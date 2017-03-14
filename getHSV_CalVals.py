import sys
import time
from networktables import NetworkTables
from constants import *
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

# NetworkTables.initialize(server='169.254.202.196')
# NetworkTables.initialize(server='127.0.0.1')
# NetworkTables.initialize(server='raspberrypi')
# NetworkTables.initialize(server='roboRIO-2016-frc.frc-robot.local')
NetworkTables.initialize(server='roborio-2016-frc.local')


time.sleep(.5)
sd=NetworkTables.getTable('SmartDashboard')


time.sleep(4)
# sd.putNumber('GearAlignAngleError', 0)
# sd.putNumber('GearAlignDistance', 0)
while True:
	print sd.getNumber('GearAlignAngleError'), sd.getNumber('GearAlignDistance')

	time.sleep(1)
