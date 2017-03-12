import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server='169.254.202.196')
# NetworkTables.initialize(server='127.0.0.1')
time.sleep(.5)

sd=NetworkTables.getTable('SmartDashboard')
# time.sleep(1)
# sd.putString('PIMode', 'RecordVideo')
sd.putString('PIMode', 'Idle')
time.sleep(1)
