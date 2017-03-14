#!/usr/bin/env python
from __future__ import division
from constants import *
from cameras import getCameras
from functions import processFrame
from networktables import NetworkTables
import RPi.GPIO as GPIO
from streamServer import app
from multiprocessing import Process
import time, traceback

import logging
logging.basicConfig(filename='/home/pi/FRC2016_Vision/output.log',level=logging.DEBUG)
logger=logging.getLogger(__name__)

def alignGear():
	logger.debug('Entered Align Gear Routine')
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	time.sleep(1)
	video = getCameras()
	dx=1000
	distINCH=1000
	theta=1000
	while True:
		try:
			# logger.debug(sd.getString(MODE_KEY))
			if not sd.getString(MODE_KEY)=='GearAlignment':
				GPIO.output(LED1_PIN, GPIO.LOW)
				GPIO.output(LED2_PIN, GPIO.LOW)
				logger.debug('Break AlignGear')
				break

			success, frame = video.read()
			processFrame(frame)
		except Exception as e:
			logger.debug(e)
			traceback.print_exc()
			raise e
		finally:
			sd.putNumber('GearAlignAngleError', theta)
			sd.putNumber('GearAlignDistance', distINCH)

def ledFlash():
	logger.debug('FlashLEDs')
	while True:
		logger.debug('FLASH')
		GPIO.output(LED1_PIN, GPIO.HIGH)
		GPIO.output(LED2_PIN, GPIO.LOW)
		time.sleep(LED_FLASH_DELAY_S)
		GPIO.output(LED1_PIN, GPIO.LOW)
		GPIO.output(LED2_PIN, GPIO.HIGH)
		time.sleep(LED_FLASH_DELAY_S)
		# if not sd.getString(MODE_KEY)=='FlashLEDs':
			# GPIO.output(LED1_PIN, GPIO.LOW)
			# GPIO.output(LED2_PIN, GPIO.LOW)
			# logger.debug('Break FlashLEDs')
			# break

def calStream():
	def worker():
		app.run(host='0.0.0.0', debug=True, use_reloader=False)
	calibration=Process(target=worker)
	calibration.start()
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	while sd.getString(MODE_KEY)=='CalibrateVision':
		pass
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)
	calibration.terminate()

def idle():
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)
	logger.debug('Idling')

def valueChanged(table, key, value, isNew):
	# logger.debug('VAL CHANGED: {}:{}'.format(key,value))
	if key==MODE_KEY:
		logger.debug('Changing MODE: {}:{}'.format(key,value))
		modes[value]()

modes={ 'GearAlignment': alignGear,
		'CalibrateVision': calStream,
		'Idle': idle,
	}

if __name__ == '__main__':
	try:
		stream=None
		running=True
		# As a client to connect to a robot
		# NetworkTables.initialize(server='roborio-2016-frc.local')
		NetworkTables.initialize(server='oconnor27')
		time.sleep(.5)
		sd = NetworkTables.getTable('SmartDashboard')
		# sd.putString(MODE_KEY, 'Idle')
		sd.addTableListener(valueChanged)
		time.sleep(.5)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(LED1_PIN, GPIO.OUT)
		GPIO.setup(LED2_PIN, GPIO.OUT)
		GPIO.output(LED1_PIN, GPIO.LOW)
		GPIO.output(LED2_PIN, GPIO.LOW)
		# alignGear()
		ledFlash()
		time.sleep(2)
		while running:
			time.sleep(1)
	except Exception as e:
		logger.error(e)
	finally:
		GPIO.cleanup()

