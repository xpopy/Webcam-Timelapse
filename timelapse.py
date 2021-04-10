import io
import os
import cv2
import sys
import time
import signal
import datetime
import PySimpleGUI as gui
from PIL import Image

# https://pysimplegui.readthedocs.io/en/latest/call%20reference/#slider-element
# https://www.geeksforgeeks.org/display-date-and-time-in-videos-using-python-opencv/



image_folder = 'img'
image_name = 'image'
image_type = 'jpg'
preview_width = 400
preview_height = 400
delay_between_photos = 5 #in seconds
next_photo_time = None


def get_latest_image(dirpath, valid_extensions=('jpg','jpeg','png')):
	"""
	Get the latest image file in the given directory
	"""
	# get filepaths of all files and dirs in the given dir
	valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
	# filter out directories, no-extension, and wrong extension files
	valid_files = [f for f in valid_files if '.' in f and \
		f.rsplit('.',1)[-1] in valid_extensions and os.path.isfile(f)]
	if not valid_files:
		return ''
	return max(valid_files, key=os.path.getmtime) 


def prepareCamera():
	camera = cv2.VideoCapture(0)
	camera.set(3, 1920)
	camera.set(4, 1080)
	return camera

def convertCV2toImage(cv2image):
	b,g,r = cv2.split(cv2image)
	tmp = cv2.merge((r,g,b))
	return Image.fromarray(tmp)

def updatePreview(window, image):
	image = convertCV2toImage(image)
	image.thumbnail((preview_width, preview_height))
	bio = io.BytesIO()
	image.save(bio, format="PNG")
	window["-IMAGE-"].update(data=bio.getvalue())

def takePicture(camera):
	return_value, cv2image = camera.read()
	return cv2image

def saveImage(image, i):
	cv2.imwrite(f'{image_folder}/{image_name}{str(i)}.jpg', image)

def setupFolder():
	folder = os.path.isdir(image_folder)
	# If folder doesn't exist, then create it.
	if not folder:
		os.makedirs(image_folder)

def main():
	setupFolder()
	layout = [
		[gui.Image(key="-IMAGE-")],
		[gui.Text(key="-LOADING-", text="Loading camera...")],
		[
			gui.Button("Test Camera"),
			gui.Button("Start Camera"),
		],
	]
	window = gui.Window("Image Viewer", layout, finalize=True)

	camera = prepareCamera()

	window["-LOADING-"].update(visible=False)

	runTimelapse = False
	time_change = datetime.timedelta(seconds=delay_between_photos)
	next_photo_time = None
	image_index = 0

	while True:	
		event, values = window.Read(timeout=1000) #1s timeout
		
		if event == "Exit" or event == gui.WIN_CLOSED:
			break

		if event == "Test Camera":
			image = takePicture(camera)
			updatePreview(window, image)

		if event == "Start Camera":
			#update image_index
			last_image = get_latest_image(image_folder)
			if last_image:
				image_index = int(last_image.replace(f'{image_folder}\{image_name}','').replace(f'.{image_type}',''))

			runTimelapse= not runTimelapse
			#show element with green or something
			
		if event == gui.TIMEOUT_KEY:
			if not runTimelapse:
				#only run if runTimelapse is True
				continue
			
			now = datetime.datetime.now()
			if next_photo_time and now < next_photo_time:
				#skip if last_photo_time exists and current time is past the next_photo time
				continue

			image = takePicture(camera)
			saveImage(image, image_index)
			updatePreview(window, image)

			image_index+= 1
			next_photo_time = now + time_change


	window.close()
if __name__ == "__main__":
	main()