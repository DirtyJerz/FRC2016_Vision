from __future__ import division
from constants import *
from cameras import getCameras
from networktables import NetworkTables
import cv2, sys
import numpy as np
import imutils, math, time
import RPi.GPIO as GPIO
import subprocess as sp
from streamServer import app
from multiprocessing import Process
import urllib

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
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	Lcap, Rcap = getCameras()
	# sd = NetworkTables.getTable('SmartDashboard')

	while True:
		# if not sd.getString('PIMode')=='GearAlignment':
			# GPIO.output(LED1_PIN, GPIO.LOW)
			# GPIO.output(LED2_PIN, GPIO.LOW)
			# print 'Break AlignGear'
			# break
		# _,lFrame=Lcap.read()
		# _,rFrame=Rcap.read()
		lFrame=getFrame(0)
		rFrame=getFrame(1)

		lparams=processFrame(lFrame)
		rparams=processFrame(rFrame)

		if len(lparams) < 1 or len(rparams) < 1:
			# no targets
			print 'No Targets'
			continue
		# For straight on bot approach, targets should be equadistant from edge of frame.
		# (Left camera [ldx]: distance of target right edge to right frame edge. Right camera [rdx]: distance of target left edge to left frame edge.)

		ldx=lFrame.shape[:2][1]-lparams[-1]['rightmost']

		rdx=rparams['leftmost']
		dx=rdx-ldx
		#write dx to network table
		print dx
		sd.putNumber('GearAlignCorrection', dx)

def ledFlash():
	print 'FlashLEDs'
	while True:
		print 'FLASH'
		GPIO.output(LED1_PIN, GPIO.HIGH)
		GPIO.output(LED2_PIN, GPIO.LOW)
		time.sleep(LED_FLASH_DELAY_S)
		GPIO.output(LED1_PIN, GPIO.LOW)
		GPIO.output(LED2_PIN, GPIO.HIGH)
		time.sleep(LED_FLASH_DELAY_S)
		if not sd.getString('PIMode')=='FlashLEDs':
			GPIO.output(LED1_PIN, GPIO.LOW)
			GPIO.output(LED2_PIN, GPIO.LOW)
			print 'Break FlashLEDs'
			# break

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
	lcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg')
	rcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_1&dummy=param.mjpg')
	fourCC=cv2.cv.CV_FOURCC(*'MJPG')
	ts=time.time()
	rightOut = cv2.VideoWriter('rightCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	leftOut = cv2.VideoWriter('leftCam_{}.avi'.format(ts), fourCC, 30.0, (WIDTH, HEIGHT))
	while(True):
		retL, lframe = lcap.read()
		retR, rframe = rcap.read()
		if retL==True and retR==True:
			leftOut.write(lframe)
			rightOut.write(rframe)
		else:	
			break

		if not sd.getString('PIMode')=='RecordVideoCV':
			break

	lcap.release()
	rcap.release()
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)

def recordVideo():
	ts=time.time()
	GPIO.output(LED1_PIN, GPIO.HIGH)
	GPIO.output(LED2_PIN, GPIO.HIGH)
	pipe1=sp.Popen('avconv -f mjpeg -i "http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg" -an -vcodec mjpeg leftCam_{}.avi'.format(ts), shell=True, stdout=sp.PIPE)
	pipe2=sp.Popen('avconv -f mjpeg -i "http://127.0.0.1:8080/?action=stream_1&dummy=param.mjpg" -an -vcodec mjpeg rightCam_{}.avi'.format(ts),shell=True, stdout=sp.PIPE)
	# pipe2=sp.Popen(cmd2,stdout=sp.PIPE)
	while True:
		if not sd.getString('PIMode')=='RecordVideo':
			pipe1.terminate()
			pipe2.terminate()
			break
		time.sleep(1)
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)

def calStream():
	
	pass
def startCameraStreams():
	global stream
	stream=sp.Popen("mjpg_streamer -i 'input_uvc.so -d /dev/video0 -f 30' -i 'input_uvc.so -d /dev/video1 -f 30' -o 'output_http.so -p 8080'", shell=True, stdout=sp.PIPE)

def killCameraStreams():
	global stream
	stream.terminate()

def idle():
	GPIO.output(LED1_PIN, GPIO.LOW)
	GPIO.output(LED2_PIN, GPIO.LOW)
	print 'Idling'

def quit():
	print 'Quit sig received'
	global running
	running=False

def valueChanged(table, key, value, isNew):
	# print 'VAL CHANGED'
	if key=='PIMode':
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
		running=True
		# As a client to connect to a robot
		NetworkTables.initialize(server='roborio-2016-frc.local')
		# NetworkTables.initialize(server='127.0.0.1')
		# NetworkTables.initialize(server='oconnor27')
		time.sleep(.5)
		sd = NetworkTables.getTable('SmartDashboard')
		# sd.putString('PIMode', 'FlashLEDs')
		# sd.addTableListener(valueChanged)
		time.sleep(.5)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(LED1_PIN, GPIO.OUT)
		GPIO.setup(LED2_PIN, GPIO.OUT)
		startCameraStreams()
		# ledFlash()
		alignGear()
		# recordVideo()
		while running:

			time.sleep(1)
	except Exception as e:
		raise e
	finally:
		GPIO.cleanup()
		killCameraStreams()

