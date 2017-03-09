import cv2
from constants import HEIGHT,WIDTH,EXPOSURE
def getCameras():
	'''
	initializes cameras 
	'''
	Lcap = cv2.VideoCapture(0)
	Rcap = cv2.VideoCapture(1)
	Lcap.set(3,WIDTH)
	Rcap.set(3,WIDTH)
	Lcap.set(4,HEIGHT)
	Rcap.set(4,HEIGHT)
	Rcap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,EXPOSURE)
	Lcap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,EXPOSURE)
	return Lcap, Rcap