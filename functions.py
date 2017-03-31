#!/usr/bin/env python
from __future__ import division
from constants import *
import cv2
import numpy as np
import imutils, traceback, logging
logging.basicConfig(filename='/home/pi/FRC2016_Vision/output.log',level=LEVEL)
logger=logging.getLogger(__name__)

def processFrame(frame):
	distINCH=1000
	theta=1000
	try:
		# logger.debug('Processing Frame')

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
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		if len(cnts)<1:
			logger.debug('Nothing Found')
			return False, distINCH, theta, frame
		comX=sum([int(c[0])*c[2] for c in centers])/sum([int(c[2]) for c in centers])
		comY=sum([int(c[1])*c[2] for c in centers])/sum([int(c[2]) for c in centers])
		logger.debug(max(np.diff([int(c[0]) for c in centers])))
		distPIX=np.abs(int(max(np.diff([int(c[0]) for c in centers])))) #distance of pixels

		distINCH=np.interp(distPIX, np.fromiter(xCAL, dtype=float),np.fromiter(yCAL, dtype=float))
		dxPIX = destX-comX

		dxINCH=(dxPIX*4.125)/(distPIX)
		theta=np.rad2deg(np.arctan2(dxINCH,distINCH))
		logger.debug( 'distINCH: {} distPIX: {} dx: {} Theta: {}'.format(np.round(distINCH, decimals=1), int(distPIX), np.round(dxINCH,decimals=1), theta))
		# logger.debug(destX-comX)
		return True, distINCH, theta, frame
	except Exception as e:
		logger.debug(e)
		return False, distINCH, theta, frame


