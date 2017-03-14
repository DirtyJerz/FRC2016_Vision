#!/usr/bin/env python
from __future__ import division
from constants import *
from cameras import getCameras
from networktables import NetworkTables
import cv2, sys, os, signal
import numpy as np
import imutils, math, time
import RPi.GPIO as GPIO
import subprocess as sp
from streamServer import app
from multiprocessing import Process
import urllib, traceback

import logging
logging.basicConfig(filename='/home/pi/FRC2016_Vision/output.log',level=logging.DEBUG)
logger=logging.getLogger(__name__)

def alignGear():
	logger.debug('here')

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
			# if not sd.getString(MODE_KEY)=='GearAlignment':
			# 	GPIO.output(LED1_PIN, GPIO.LOW)
			# 	GPIO.output(LED2_PIN, GPIO.LOW)
			# 	# startCameraStreams()
			# 	logger.debug('Break AlignGear')
			# 	break

			success, frame = video.read()
			height, width = frame.shape[:2]
			destX=width/2
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
			cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cnts = cnts[0] if imutils.is_cv2() else cnts[1]
			centers=[]
			for c in cnts:
				params={}
				# compute the moments of the contour
				M = cv2.moments(c)
				#filter smaller shapes
				if M["m00"]<50:
					continue        		  
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]), int(M["m00"]))
				centers.append(center)
				# draw the contour and center of the shape on the image
				# cv2.drawContours(frame, [c], -1, (0, 255, 100), 2)
			# We are using Motion JPEG, but OpenCV defaults to capture raw images,
			# so we must encode it into JPEG in order to correctly display the
			# video stream.


			comX=sum([int(c[0])*c[2] for c in centers])/sum([int(c[2]) for c in centers])
			comY=sum([int(c[1])*c[2] for c in centers])/sum([int(c[2]) for c in centers])
			distPIX=np.abs(int(np.diff([int(c[0]) for c in centers]))) #distance of pixels
			distINCH=np.interp(distPIX, np.fromiter(xCAL, dtype=float),np.fromiter(yCAL, dtype=float))
			dxPIX = destX-comX
			dxINCH=(dxPIX*4.125)/(distPIX)
			theta=np.rad2deg(np.arctan2(dxINCH,distINCH))
			# logger.debug( 'distINCH: {} distPIX: {} dx: {} Theta: {}'.format(np.round(distINCH, decimals=1), int(distPIX), np.round(dxINCH,decimals=1), theta))
			# cv2.circle(frame, (comX, comY), 2, (0, 0, 255), -1)
			# cv2.putText(frame, 'dist: {} dx: {} Theta: {}'.format(np.round(distINCH, decimals=1), np.round(dxINCH,decimals=1), theta), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,255,255),2)
			# logger.debug(destX-comX)



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
		if not sd.getString(MODE_KEY)=='FlashLEDs':
			GPIO.output(LED1_PIN, GPIO.LOW)
			GPIO.output(LED2_PIN, GPIO.LOW)
			logger.debug('Break FlashLEDs')
			break

def getFrame(camera):
	stream=urllib.urlopen('http://127.0.0.1:8080/?action=stream_{}&dummy=param.mjpg'.format(camera))
	bytes=''
	while True:
	    bytes+=stream.read(1024)
	    a = bytes.find('\xff\xd8')
	    b = bytes.find('\xff\xd9')
	    if a!=-1 and b!=-1:
	        jpg = bytes[a:b+2]
	        bytes= bytes[b+2:]
	        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
	        return i

def recordVideoCV():
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	killCameraStreams()	
	time.sleep(1)
	lcap = getCameras()
	fourCC=cv2.cv.CV_FOURCC(*'MJPG')
	ts=time.time()
	# rightOut = cv2.VideoWriter('/home/pi/videos/rightCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	leftOut = cv2.VideoWriter('/home/pi/videos/leftCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	while(True):
		retL, lframe = lcap.read()
		retR, rframe = rcap.read()
		if retL==True and retR==True:
			leftOut.write(lframe)
			rightOut.write(rframe)
		else:	
			break

		if not sd.getString(MODE_KEY)=='RecordVideoCV':
			break

	lcap.release()
	rcap.release()
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)



def recordVideoMJPGStream():
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	lcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg')
	# rcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_1&dummy=param.mjpg')
	fourCC=cv2.cv.CV_FOURCC(*'MJPG')
	ts=time.time()
	rightOut = cv2.VideoWriter('/home/pi/videos/rightCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	# leftOut = cv2.VideoWriter('/home/pi/videos/leftCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	while(True):
		retL, lframe = lcap.read()
		retR, rframe = rcap.read()
		if retL==True and retR==True:
			leftOut.write(lframe)
			rightOut.write(rframe)
		else:	
			break

		if not sd.getString(MODE_KEY)=='RecordVideoMJPG':
			break

	lcap.release()
	rcap.release()
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)

def recordVideo():
	ts=time.time()
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	pipe1=sp.Popen('avconv -f mjpeg -i "http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg" -an -vcodec mjpeg /home/pi/videos/leftCam_{}.avi'.format(ts), shell=True, stdout=sp.PIPE)
	# pipe2=sp.Popen('avconv -f mjpeg -i "http://127.0.0.1:8080/?action=stream_1&dummy=param.mjpg" -an -vcodec mjpeg /home/pi/videos/rightCam_{}.avi'.format(ts),shell=True, stdout=sp.PIPE)
	# pipe2=sp.Popen(cmd2,stdout=sp.PIPE)
	while True:
		if not sd.getString(MODE_KEY)=='RecordVideo':
			os.kill(pipe1.pid)
			os.kill(pipe2.pid)
			break
		time.sleep(1)
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)

def calStream():
	killCameraStreams()
	logger.debug(stream.wait())
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
	startCameraStreams()

def startCameraStreams():
	global stream
	stream=sp.Popen("mjpg_streamer -i 'input_uvc.so -d /dev/video0 -f 30 -ex 0' -o 'output_http.so -p 8080'", shell=True, stdout=sp.PIPE,preexec_fn=os.setsid)
	# stream=sp.Popen("mjpg_streamer -i 'input_uvc.so -d /dev/video0 -f 30 -ex 0' -i 'input_uvc.so -d /dev/video1 -f 30 -ex 0' -o 'output_http.so -p 8080'", shell=True, stdout=sp.PIPE,preexec_fn=os.setsid)
	logger.debug('stream started PID:{}'.format(stream.pid))

def killCameraStreams():
	pass
	# logger.debug('killing mjpg stream')
	# global stream
	# stream.terminate()
	# logger.debug(stream.pid)
	# os.killpg(stream.pid,signal.SIGINT)


def idle():
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)
	logger.debug('Idling')

def quit():
	logger.debug('Quit sig received')
	global running
	running=False

def valueChanged(table, key, value, isNew):
	# logger.debug('VAL CHANGED: {}:{}'.format(key,value))
	if key==MODE_KEY:
		logger.debug('Changing MODE: {}:{}'.format(key,value))
		modes[value]()

modes={ 'GearAlignment': alignGear,
		'FlashLEDs': ledFlash,
		'RecordVideo': recordVideo,
		'RecordVideoCV': recordVideoCV,
		'CalibrateVision': calStream,
		'Idle': idle,
		'Quit':quit,
	}

if __name__ == '__main__':
	try:
		stream=None
		running=True
		# As a client to connect to a robot
		# NetworkTables.initialize(server='roboRIO-2016-frc.frc-robot.local')
		NetworkTables.initialize(server='roborio-2016-frc.local')
		# NetworkTables.initialize(server='127.0.0.1')
		# NetworkTables.initialize(server='oconnor27')
		time.sleep(.5)
		sd = NetworkTables.getTable('SmartDashboard')
		# sd.putString(MODE_KEY, 'Idle')
		sd.putString('showCalResult', 'True')
		sd.addTableListener(valueChanged)
		time.sleep(.5)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(LED1_PIN, GPIO.OUT)
		GPIO.setup(LED2_PIN, GPIO.OUT)
		GPIO.output(LED1_PIN, GPIO.LOW)
		GPIO.output(LED2_PIN, GPIO.LOW)
		# startCameraStreams()
		alignGear()
		time.sleep(2)
		try:
			modes[sd.getString(MODE_KEY)]()
		except Exception as e:
			pass
		while running:
			time.sleep(1)
	except Exception as e:
		raise e
	finally:
		GPIO.cleanup()
		killCameraStreams()

