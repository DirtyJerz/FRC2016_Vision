import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

# NetworkTables.initialize(server='169.254.202.196')
# NetworkTables.initialize(server='127.0.0.1')
# NetworkTables.initialize(server='')
NetworkTables.initialize(server='roborio-2016-frc.local')

time.sleep(.5)

sd=NetworkTables.getTable('SmartDashboard')
# time.sleep(1)
# sd.putString('PIMode', 'RecordVideo')

# sd.putString('PIMode', 'RecordVideoCV')
# sd.putString('PIMode', 'stream')
# sd.putString('PIMode', 'calibrate')
# print sd.getString('PIMode')
sd.putString('PIMode', 'Idle')
# sd.putString('PIMode', 'FlashLEDs')
# sd.putString('PIMode', 'Quit')
time.sleep(1)
