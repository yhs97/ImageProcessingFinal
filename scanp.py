# USAGE
# python scan1.py --image images/page.jpg


from transformp.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
import sys
from PIL import Image
def scanflask(imagepath, uniqueName, scannedPath):

	image = cv2.imread(imagepath)
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)

	# convert the image to grayscale, blur it, and find edges
	# in the image
	#gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
	hsv=cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
	hue, saturation, value = cv2.split(hsv)
	#clahe1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	#cl2 = clahe1.apply(gray)
	#value = cv2.GaussianBlur(value, (3, 3), 0)
	#print(gray.shape)
	value = cv2.medianBlur(value,5)
	#value = cv2.bilateralFilter(value,5,75,75)
	th = cv2.adaptiveThreshold(value,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
				cv2.THRESH_BINARY,11,2)
	#retval, th = cv2.threshold(value, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

	thresholded_open = cv2.morphologyEx(th, cv2.MORPH_OPEN, (5,5))
	thresholded_close = cv2.morphologyEx(thresholded_open, cv2.MORPH_CLOSE, (5,5))

	#kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
	#dilated = cv2.dilate(th, kernel, iterations=2)
	#edged = cv2.Canny(thresholded_close, 5, 15)

	edged = cv2.Laplacian(thresholded_close,cv2.CV_8UC1)
	#kernel = np.ones((5,5),np.uint8)
	#erosion = cv2.erode(edged,kernel,iterations = 1)
	#dilation = cv2.dilate(edged,kernel,iterations = 1)


	# show the original image and the edge detected image

	print("STEP 1: Edge Detection")


	#edged.save(os.path.join(app.config['UPLOAD_FOLDER'], 'edged'))
	cv2.imwrite(scannedPath+"edges.jpg",edged)

	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.05 * peri, True)

		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break


	def step3():
		warped = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)

		kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
		im=cv2.filter2D(orig,-1,kernel)
		

		imginv=cv2.bitwise_not(im.copy())

		T = threshold_local(warped , 25, offset = 10, method = "gaussian")
		warped = (warped > T).astype("uint8") * 255
		#equ = cv2.equalizeHist(warped)

		
		print("STEP 3: Apply perspective transform")
		#cv2.imshow("Original", imutils.resize(orig, height = 650))
		
		cv2.imwrite(scannedPath+uniqueName+"_clear.jpg",im)
		cv2.imwrite(scannedPath+uniqueName+"_inverted.jpg",imginv)
		cv2.imwrite(scannedPath+uniqueName+"_scanned.jpg",warped)



	try:
		screenCnt

	except NameError:
		step3()


	else:
		if cv2.contourArea(screenCnt)<10500:
			step3()
		# show the contour (outline) of the piece of paper
		print(cv2.contourArea(screenCnt))
		print("STEP 2: Find contours of paper")
		print(screenCnt)
		cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
		#cv2.imshow("Outline", image)

		cv2.imwrite(scannedPath+"outline.jpg",image)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()
		
		# apply the four point transform to obtain a top-down
		# view of the original image
		warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

		# convert the warped image to grayscale, then threshold it
		# to give it the black and white paper effect
		
		kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
		im=cv2.filter2D(warped,-1,kernel)



		warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
		T = threshold_local(warped, 11, offset = 10, method = "gaussian")
		warped = (warped > T).astype("uint8") * 255
		
		#kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
		#warped=cv2.filter2D(warped,-1,kernel)

		print("STEP 3: Apply perspective transform")
		#cv2.imshow("Original", imutils.resize(orig, height = 650))

		cv2.imwrite(scannedPath+uniqueName+"_scanned.jpg",warped)
		cv2.imwrite(scannedPath+uniqueName+"_clear.jpg",im)

		#cv2.imshow("Clear", imutils.resize(im, height = 650))
		#cv2.waitKey(0)

