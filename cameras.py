import cv2, imutils, time, logging
from constants import *
from networktables import NetworkTables
logging.basicConfig(filename='/home/pi/FRC2016_Vision/output.log',level=logging.DEBUG)
logger=logging.getLogger(__name__)

def getCameras():
	'''
	initializes cameras 
	'''
	while True:
		logger.debug('Trying to open camera...')
		cap = cv2.VideoCapture(0)
		if cap.isOpened():
			break
		time.sleep(1)
		# cap=cv2.VideoCapture('http://127.0.0.1:8080/?action=stream_0&dummy=param.mjpg')
		# cap.set(3,WIDTH)
		# cap.set(4,HEIGHT)
	cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,EXPOSURE)
	logger.debug('Camera opened...Returning to main thread.')
	return cap

class USBVideoCamera(object):
	def __init__(self):
		self.video = getCameras()
	
	def __del__(self):
		self.video.release()

	def get_frame(self, idx):
		success, frame = self.video.read()
		height, width = frame.shape[:2]
		destX=width/2
		destY=height/2
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		if self.sd.getString('showCalResult')=='True':
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

				ret, jpeg = cv2.imencode('.jpg', frame)
				return jpeg.tostring()
		else: 
			cv2.circle(frame, (destX, destY), 2, (0, 0, 255), -1)
			cv2.putText(frame, 'HSV= {}'.format(hsv[destY, destX]), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,255,255),2)
			ret, jpeg = cv2.imencode('.jpg', frame)
			return jpeg.tostring()