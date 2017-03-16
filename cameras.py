import cv2
import imutils
from constants import *

def getCameras():
	'''
	initializes cameras 
	'''
	Lcap = cv2.VideoCapture(0)
	Rcap = cv2.VideoCapture(1)
	# Lcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg')
	# Rcap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_1&dummy=param.mjpg')
	Lcap.set(3,WIDTH)
	Rcap.set(3,WIDTH)
	Lcap.set(4,HEIGHT)
	Rcap.set(4,HEIGHT)
	Rcap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,EXPOSURE)
	Lcap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,EXPOSURE)
	return Lcap, Rcap

class USBVideoCamera(object):
	def __init__(self):
		# Using OpenCV to capture from device 0. If you have trouble capturing
		# from a webcam, comment the line below out and use a video file
		# instead.
		self.video = getCameras()
		# If you decide to use video.mp4, you must have this file in the folder
		# as the main.py.
		# self.video = cv2.VideoCapture('video.mp4')
	
	def __del__(self):
		self.video[0].release()
		self.video[1].release()

	def get_frame(self, idx, hsvFrames=False):
		success, frame = self.video[idx].read()
		height, width = frame.shape[:2]
		destX=width/2
		destY=height/2
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		if not hsvFrames:
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
			cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cnts = cnts[0] if imutils.is_cv2() else cnts[1]
			for c in cnts:
				# compute the moments of the contour
				M = cv2.moments(c)
				#filter smaller shapes
				if M["m00"]<50:
					continue        		                
				# draw the contour and center of the shape on the image
				cv2.drawContours(frame, [c], -1, (0, 255, 100), 2)
			# We are using Motion JPEG, but OpenCV defaults to capture raw images,
			# so we must encode it into JPEG in order to correctly display the
			# video stream.
			ret, jpeg = cv2.imencode('.jpg', frame)
			# ret, jpeg = cv2.imencode('.jpg', thresh)
			return jpeg.tostring()
		else: 
			cv2.circle(frame, (destX, destY), 2, (0, 0, 255), -1)
			# print hsv[destY, destX]
			ret, jpeg = cv2.imencode('.jpg', frame)
			return jpeg.tostring()