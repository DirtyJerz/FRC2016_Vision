#!/usr/bin/env python
from __future__ import division
from constants import *
import cv2
import numpy as np
import imutils

def processFrame(frame):
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
		cv2.drawContours(frame, [c], -1, (0, 255, 100), 2)
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
	cv2.circle(frame, (comX, comY), 2, (0, 0, 255), -1)
	cv2.putText(frame, 'dist: {} dx: {} Theta: {}'.format(np.round(distINCH, decimals=1), np.round(dxINCH,decimals=1), theta), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,255,255),2)
	# logger.debug(destX-comX)
	return distINCH, theta, frame

