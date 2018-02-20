import cv2
import numpy as np
from main import Camera

image_hsv = None   # global ;(
pixel = (20,60,80) # some stupid default
upper = np.array([40,180,180])
lower = np.array([20,120,100])
# mouse callback function
def pick_color(event,x,y,flags,param):
	global upper, lower
	if event == cv2.EVENT_LBUTTONDOWN:
		pixel = image_hsv[y,x]

		#you might want to adjust the ranges(+-10, etc):
		upper =  np.array([pixel[0] + 20, pixel[1] + 20, pixel[2] + 80])
		lower =  np.array([pixel[0] - 20, pixel[1] - 20, pixel[2] - 80])
		print(pixel, lower, upper)



def main():
	import sys
	global image_hsv, pixel, upper, lower # so we can use it in mouse callback
	cam = Camera()

	while True:
		# image_src = cv2.imread(sys.argv[1])  # pick.py my.png
		image_src = cam.get_frame()
		if image_src is None:
			print ("the image read is None............")
			return
		cv2.imshow("bgr",image_src)

		## NEW ##
		cv2.namedWindow('hsv')
		cv2.setMouseCallback('hsv', pick_color)

		# now click into the hsv img , and look at values:
		image_hsv = cv2.cvtColor(image_src,cv2.COLOR_BGR2HSV)
		cv2.imshow("hsv",image_hsv)
		image_mask = cv2.inRange(image_hsv,lower,upper)
		cv2.imshow("mask",image_mask)
		cv2.waitKey(1)
	cv2.destroyAllWindows()

if __name__=='__main__':
	main()