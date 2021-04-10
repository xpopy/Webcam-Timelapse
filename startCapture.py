import os
import cv2
import sys
import time
import signal
import datetime


camera = cv2.VideoCapture(0)
camera.set(3, 1920)
camera.set(4, 1080)
signal.signal(signal.SIGINT, signal.default_int_handler)


# CAP_PROP_APERTURE
# CAP_PROP_AUTOFOCUS
# CAP_PROP_AUTO_EXPOSURE
# CAP_PROP_AUTO_WB
# CAP_PROP_BACKEND
# CAP_PROP_BACKLIGHT
# CAP_PROP_BRIGHTNESS
# CAP_PROP_CONTRAST
# CAP_PROP_EXPOSURE
# CAP_PROP_FOCUS
# CAP_PROP_FRAME_HEIGHT
# CAP_PROP_FRAME_WIDTH
# CAP_PROP_GAMMA
# CAP_PROP_ISO_SPEED
# CAP_PROP_SATURATION
# CAP_PROP_SHARPNESS

try:
	i = 0
	while True:
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d %H-%M-%S")

		print("taking photo " + str(i))
		return_value, image = camera.read()

		#cv2.imwrite('img/' + date + ' ' + str(i)  +'.jpg', image)
		cv2.imwrite('img/image' + str(i)  +'.jpg', image)
		i += 1

		time.sleep(0.1)

except KeyboardInterrupt:
		print("Bye")
		del(camera)
		sys.exit()

