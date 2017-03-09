from __future__ import division
import cv2 
import numpy as np
import imutils, math, time
from constants import *
from cameras import getCameras
from networktables import NetworkTables
# import RPi.GPIO as GPIO

import logging
logging.basicConfig(level=logging.DEBUG)



def processFrame(frame):
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
	cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	c2X=0
	dicts=[]
	for c in cnts:
		# compute the moments of the contour
		M = cv2.moments(c)
		#filter smaller shapes
		if M["m00"]<50:
			continue

		params={}
		params['leftmost'] = tuple(c[c[:,:,0].argmin()][0])
		params['rightmost'] = tuple(c[c[:,:,0].argmax()][0])
		params['width']=params['rightmost'][0]-params['leftmost'][0]
		topmost = tuple(c[c[:,:,1].argmin()][0])
		params['bottmost'] = tuple(c[c[:,:,1].argmax()][0])
		params['cx'] = int(M["m10"] / M["m00"])
		params['cy'] = int(M["m01"] / M["m00"])	
		dicts.append(params)
		cv2.drawContours(frame, [c], -1, (0, 255, 100), 2)

	return dicts

def alignGear():
	Lcap, Rcap = getCameras()
	sd = NetworkTables.getTable('SmartDashboard')

	while True:
		
		_,lFrame=Lcap.read()
		_,rFrame=Rcap.read()

		lparams=processFrame(lFrame)
		rparams=processFrame(rFrame)
		if len(lparams) < 1 or len(rparams) < 1:
			# no targets
			continue
		# For straight on bot approach, targets should be equadistant from edge of frame.
		# (Left camera [ldx]: distance of target right edge to right frame edge. Right camera [rdx]: distance of target left edge to left frame edge.)

		ldx=lFrame.shape[:2][1]-lparams[-1]['rightmost']
		rdx=rparams['leftmost']
		dx=rdx-ldx
		#write dx to network table
		sd.putNumber('gearAlignCorrection', 2)


def ledFlash():
	pass

def recordVideo():
	global running
	running=True
	print 'Recording Video'
	lcap, rcap = getCameras()
	fourCC=cv2.cv.CV_FOURCC(*'XVID')
	rightOut = cv2.VideoWriter('rightCam.avi', fourCC, 20.0, (WIDTH, HEIGHT))
	leftOut = cv2.VideoWriter('leftCam.avi', fourCC, 20.0, (WIDTH, HEIGHT))
	i=0
	while(rcap.isOpened() and lcap.isOpened()):
		retL, lframe = lcap.read()
		retR, rframe = rcap.read()
		if retL==True and retR==True:
			leftOut.write(lframe)
			cv2.imshow('frame',lframe)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		else:
			break
		i+=1
		if i>20:
			if not sd.getString('opMode')=='RecordVideo':
				break
			i=0

	lcap.release()
	rcap.release()
	cv2.destroyAllWindows()

def serveVideo():
	# steram gear cams to DS?
	pass

def idle():
	print 'Idling'


def valueChanged(table, key, value, isNew):
	# print 'VAL CHANGED'
	if key=='opMode':
		modes[value]()

modes={ 'GearAlignment': alignGear,
		'FlashLEDs': ledFlash,
		'RecordVideo': recordVideo,
		'Idle': idle,
	}
	
if __name__ == '__main__':
	running=False
	# As a client to connect to a robot
	NetworkTables.initialize(server='127.0.0.1')
	time.sleep(.5)
	sd = NetworkTables.getTable('VisionTable')
	sd.addTableListener(valueChanged)
	time.sleep(.5)
	while True:
		time.sleep(1)

