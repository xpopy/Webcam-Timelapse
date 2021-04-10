import os
import cv2

image_folder = 'img'
image_type = 'jpg'
video_name = 'timelapse'
video_extension = 'mp4'
codec = 'mpeg4'
fps = 10
bitrate = '50000k'

def convertToVideoFFMPEG():
	os.system(f'ffmpeg -r {fps} -i "{image_folder}/image%d.{image_type}" -vcodec {codec} -b {bitrate} -y {video_name}.{video_extension}')

convertToVideoFFMPEG()