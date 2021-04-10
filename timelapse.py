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



image_folder = 'img'
image_type = 'jpg'
preview_width = 400
preview_height = 400


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

def updatePreview(window, image):
	image.thumbnail((preview_width, preview_height))
	bio = io.BytesIO()
	image.save(bio, format="PNG")
	window["-IMAGE-"].update(data=bio.getvalue())

def takePicture(camera):
	return_value, cv2image = camera.read()
	b,g,r = cv2.split(cv2image)
	img = cv2.merge((r,g,b))
	return Image.fromarray(img)

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

	lastImage = ''
	runTimelapse = False
	runTest = False
	while True:	
		event, values = window.Read(timeout=1000) #60s timeout
		
		if event == "Exit" or event == gui.WIN_CLOSED:
			break

		if event == "Test Camera":
			runTest = not runTest
			runTimelapse = False

		if event == "Start Camera":
			runTimelapse= not runTimelapse
			runTest = False
			#show element with green or something
			

		if event == gui.TIMEOUT_KEY:
			if runTest:
				#Show live view of camera
				image = takePicture(camera)
				updatePreview(window, image)
				continue

			if not runTimelapse:
				continue
			
			last_image = get_latest_image(image_folder)

			if not last_image:
				continue

			if last_image == lastImage:
				continue

			lastImage = last_image
			image = Image.open(last_image)
			updatePreview(window, image)


	window.close()
if __name__ == "__main__":
	main()