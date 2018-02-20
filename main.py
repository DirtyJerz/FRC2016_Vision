#!/usr/bin/env python
# 'http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg'
import os, sys
import threading
import psutil
import logging
from time import sleep, time
import subprocess as sp
import cv2
from networktables import NetworkTables
from constants import *
import imutils
from gpiozero import LED

logging.basicConfig(filename='/home/pi/FRC2016_Vision/output.log',level=logging.DEBUG)
logger=logging.getLogger(__name__)

with open('/home/pi/FRC2016_Vision/output.log', 'w'):
	pass

MODE_KEY='vision_mode'
HEIGHT=480
WIDTH=640

led=LED(5)
led.off()

class Camera(object):
	def __init__(self):
		self.frame = ''
		led.on()		
		sp.Popen('/usr/bin/v4l2-ctl -c exposure_auto=1', shell=True, stdout=sp.PIPE)
		sp.Popen('/usr/bin/v4l2-ctl -c brightness=133', shell=True, stdout=sp.PIPE)
		sp.Popen('/usr/bin/v4l2-ctl -c saturation=200', shell=True, stdout=sp.PIPE)
		sp.Popen('/usr/bin/v4l2-ctl -c contrast=10', shell=True, stdout=sp.PIPE)
		self.frameReady = False
		self.fgThreadRunning = True        
		self.fgThread = threading.Thread(target=self.frameGrabber, args=())
		self.fgThread.start()

	def __del__(self):
		led.off()
		cv2.destroyAllWindows()

	def frameGrabber(self):
		import requests
		import numpy as np

		r = requests.get('http://vision:8080/?action=stream_0&dummy=param.mjpg', stream=True)
		if(r.status_code == 200):
			bytes = ''
			for chunk in r.iter_content(chunk_size=1024):
				if not self.fgThreadRunning:
					return
				bytes += chunk
				a = bytes.find(b'\xff\xd8')
				b = bytes.find(b'\xff\xd9')
				if a != -1 and b != -1:
					jpg = bytes[a:b+2]
					bytes = bytes[b+2:]
					image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
					self.frameReady = True
					self.frame = image
		else:
			self.frameReady = False
			logger.error("Received unexpected status code {}".format(r.status_code))
			if not self.fgThreadRunning:
				logger.debug('Exiting Thread')
				return

	def get_frame(self):
		while not self.frameReady:
			logger.info('Waiting for frame')
			sleep(1)
		return self.frame

def findRetroTape():
	cam = Camera()
	while True:
		frame = cam.get_frame()
		height, width = frame.shape[:2]
		destX = width/2
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
		cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		centers=[]
		for c in cnts:
			params={}
			cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
			# compute the moments of the contour
			M = cv2.moments(c)
			#filter smaller shapes
			if M["m00"]<50:
				continue        		  
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]), int(M["m00"]))
			print destX - center[0]

		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
		# cv2.imshow("frame", frame)
		
		if len(cnts)<1:
			logger.debug('Nothing Found')
		# return frame
		# TODO: Write destX - center[0]

def findCube():
	led.on()
	cam = Camera()

	while True:
		frame = cam.get_frame()
		height, width = frame.shape[:2]
		destX = width/2
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, (H[0], S[0], V[0]), (H[1], S[1], V[1]))
		cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		for c in cnts: # Filter the contours
			area = cv2.contourArea(c)
			if (area < 10000): # FILTER BY AREA
				continue
			if (cv2.arcLength(c, True) < 80): # FILTER BY PERIMITER
				continue
			hull = cv2.convexHull(c)
			solid = 100 * area / cv2.contourArea(hull)
			if (solid < 67 or solid > 100): #FILTER BY SOLIDITY
				continue
			c = hull
			cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
			# compute the moments of the contour
			M = cv2.moments(c)
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])

			print destX - cX
		# cv2.imshow("frame", frame)
		# cv2.waitKey(1)
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		if len(cnts)<1:
			logger.debug('Nothing Found')
		# return frame
		# TODO: Write destX - center[0]

def valueChanged(table, key, value, isNew):
	if key==MODE_KEY:
		logger.debug('Changing MODE: {}:{}'.format(key,value))
		modes[value]()

def recordVideo():
	sp.Popen('/usr/bin/v4l2-ctl -c exposure_auto=1', shell=True, stdout=sp.PIPE)
	sp.Popen('/usr/bin/v4l2-ctl -c brightness=133', shell=True, stdout=sp.PIPE)
	sp.Popen('/usr/bin/v4l2-ctl -c saturation=200', shell=True, stdout=sp.PIPE)
	sp.Popen('/usr/bin/v4l2-ctl -c contrast=10', shell=True, stdout=sp.PIPE)
	cap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg')
	fourCC=cv2.cv.CV_FOURCC(*'MJPG')
	ts=time()
	outfile = cv2.VideoWriter('/home/pi/recordings/Recording_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	while(True):
		ret, frame = cap.read()
		if ret==True:
			print len(frame)
			outfile.write(frame)
		else:	
			break

		if not sd.getString(MODE_KEY,'')=='recordVideo':
			break

	cap.release()

def idle():
	while True:
		sleep(0.1)
		if not sd.getString(MODE_KEY,'idle')=='idle':
			break
		blinkLED(1, 0.0001, False)

def blinkLED(times, duration, endOn):	
	for x in range(times):
		led.off()
		sleep(duration)
		led.on()
		sleep(duration)
	if not endOn:
		led.off()

modes={ 'Idle': idle,
		'Record': recordVideo,
		'FindStrip': findRetroTape,
		'FindCube': findCube
	}


if __name__ == '__main__':
	blinkLED(2, 0.25, True)
	NetworkTables.initialize(server='roborio-2016-frc.local')
	sd = NetworkTables.getTable('SmartDashboard')
	sd.addTableListener(valueChanged)
	idle()
	# applyFilter('testFilter1')

	# recordVideo()
