import io
import os
import cv2
import datetime
import PySimpleGUI as gui
from PIL import Image

# https://pysimplegui.readthedocs.io/en/latest/call%20reference/#slider-element
# https://www.geeksforgeeks.org/display-date-and-time-in-videos-using-python-opencv/


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
	cv2image_rgb = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB) 
	return Image.fromarray(cv2image_rgb)

def updatePreview(window, image, preview_width, preview_height):
	image = convertCV2toImage(image)
	image.thumbnail((preview_width, preview_height))
	bio = io.BytesIO()
	image.save(bio, format="PNG")
	window["-IMAGE-"].update(data=bio.getvalue())

def takePhoto(camera, add_date=False):
	return_value, cv2image = camera.read()
	if add_date:
		font = cv2.FONT_HERSHEY_DUPLEX
		date_now = datetime.datetime.now()
		formatted_date_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
		#Add the text on top of the image
		frame = cv2.putText(cv2image, formatted_date_now,
							(30, 50),
							font, 1,
							(50, 205, 50), 
							4, cv2.LINE_8)
	return cv2image

def saveImage(image_folder, image_name, image_type, image, i):
	cv2.imwrite(f'{image_folder}/{image_name}{str(i)}.{image_type}', image)

def setStatus(window, text):
	window["-STATUS-"].update(value=text)

def updateCountdown(window, next_photo_time):
	now = datetime.datetime.now()
	time_left = next_photo_time - now
	if time_left > datetime.timedelta(0):
		#Only update timer if it's positive
		window['-TIME-LEFT-'].update(value = str(time_left).split(".")[0])

def setupFolder(image_folder):
	folder = os.path.isdir(image_folder)
	# If folder doesn't exist, then create it.
	if not folder:
		os.makedirs(image_folder)

def main():

	#Default settings
	image_folder = 'img'
	image_name = 'image'
	image_type = 'jpg'
	preview_width = 600
	preview_height = 800
	delay_between_photos = 5 #in seconds
	overlay_date_on_images = True
	
	#Create the image folder if it doesn't exist
	setupFolder(image_folder)

	#The layout of GUI
	layout = [
		[gui.Text(key="-TIME-LEFT-", text="", size=(40, 1))],
		[gui.Image(key="-IMAGE-")],
		[gui.Text(key="-STATUS-", text="", size=(40, 1))],
		[	
			gui.Input(key='-INPUT-DELAY-', enable_events=True, size = (6, None)), 
			gui.Text(key="-INPUT-DELAY-DESC-", text="Delay in s (ex: 60 = a photo every minute)"),
		],
		[
			gui.Button("Test Camera"),
			gui.Button("Start Camera"),
		],
	]
	window = gui.Window("Timelapse", layout, finalize=True)


	#Load the camera, can take a few seconds depending on camera
	setStatus(window, "Loading camera, this might take a while...")
	camera = prepareCamera()
	setStatus(window, "Camera loaded, select your move...")

	#Set up some variables
	runTimelapse = False
	time_change = datetime.timedelta(seconds=delay_between_photos)
	next_photo_time = None
	image_index = 0

	while True:	
		event, values = window.Read(timeout=1000) #1s timeout
		
		if event == "Exit" or event == gui.WIN_CLOSED:
			#Always keep a way out
			break

		if event == "Test Camera":
			#Takes a photo and updates the preview
			image = takePhoto(camera, overlay_date_on_images)
			updatePreview(window, image, preview_width, preview_height)

		if event == "Start Camera":

			#Make sure -INPUT-DELAY- is set
			if len(values['-INPUT-DELAY-']) == 0:
				setStatus(window, "You need to set the delay between photos first")
				window["-INPUT-DELAY-"].set_focus()
				continue

			#Reset next_photo_time
			next_photo_time = None

			#Update image_index from the last saved image
			last_image = get_latest_image(image_folder)
			if last_image:
				image_index = int(last_image.replace(f'{image_folder}\{image_name}','').replace(f'.{image_type}',''))
				image_index += 1 # add one so we don't replace the last image

			#Start/stop timelapse
			if runTimelapse:
				setStatus(window, "Timelapse stopped")
				runTimelapse = False
			else:
				setStatus(window, "Timelapse running...")
				runTimelapse = True
		
		if event == '-INPUT-DELAY-':
			val = values['-INPUT-DELAY-']
			if not val or len(val) == 0:
				#There's no value, skip
				continue
			
			if val[-1] not in ('0123456789.'):
				#The last character input is not a number or dot, illegal. No characters allowed in here
				window['-INPUT-DELAY-'].update(val[:-1])
				continue

			if len(val) > 5:
				#Max 5 characters please, I can't take more than that
				window['-INPUT-DELAY-'].update(val[:-1])
				continue

			#Finally we can set our delay_between_photos
			delay_between_photos = int(val)
			time_change = datetime.timedelta(seconds=delay_between_photos)
			
		if event == gui.TIMEOUT_KEY:
			#only run if runTimelapse is True
			if not runTimelapse:
				continue
			
			if next_photo_time:
				updateCountdown(window, next_photo_time)

			now = datetime.datetime.now()
			#skip if last_photo_time exists and current time is past the next_photo time
			if next_photo_time and now < next_photo_time:
				continue

			#Take a photo, save it to disk and update the preview with it
			image = takePhoto(camera, overlay_date_on_images)
			saveImage(image_folder, image_name, image_type, image, image_index)
			updatePreview(window, image, preview_width, preview_height)

			#Increment image index for name, and set time for next photo
			image_index+= 1
			next_photo_time = now + time_change

			updateCountdown(window, next_photo_time)


	window.close()
if __name__ == "__main__":
	main()