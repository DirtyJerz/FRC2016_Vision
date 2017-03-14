#!/usr/bin/env python 
import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.setServerMode()
sd=NetworkTables.getTable('SmartDashboard')
sd.putNumber('GearAlignCorrection', 0)
sd.putString('PIMode2', 'Idle')
while True:
	time.sleep(1)