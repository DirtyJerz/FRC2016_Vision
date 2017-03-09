import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.setServerMode()
sd=NetworkTables.getTable('VisionTable')
sd.putNumber('GearAlignCorrection', 0)
sd.putString('opMode', 'Idle')
while True:
	time.sleep(1)