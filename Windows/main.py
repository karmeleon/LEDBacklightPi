import time, socket, math, multiprocessing
import PIL.ImageGrab as ig
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import numpy as np

def main():
	#print(timeit.timeit('get_dominant_color(2)', 'from __main__ import get_dominant_color', number=50) / 50)
	#return

	# static DHCP allocation of RPi
	address = input("IP address of Raspberry Pi?")
	if address == "":
		address = "192.168.1.120"

	sock = socket.socket()
	port = 1420

	sock.connect((address, port))

	last_color = LabColor(0.0, 0.0, 0.0)
	delta_e_threshold = 5.0
	max_wait_time = 2.0	# seconds
	min_wait_time = 0.033	# seconds
	last_change_time = time.time()

	allow_throttling = False

	while True:
		#time.sleep(1)
		image = ig.grab()
		w, h = image.size
		image.thumbnail((int(w / 20), int(h / 20)))
		color = img_avg(np.array(image))

		if allow_throttling:
			# find dE from previous color
			srgb_color = sRGBColor(*color, is_upscaled=True)
			# convert to LAB color
			lab_color = convert_color(srgb_color, LabColor, target_illuminant='d50')
			# get dE
			delta_e = delta_e_cie2000(lab_color, last_color)

			# if the color change is above the threshold, send the new color and reset the clock
			if delta_e >= delta_e_threshold:
				last_color = lab_color
				last_change_time = time.time()
				send_color(color, sock)
			else:
				# otherwise wait a bit before looking again based off how long it's been since a change
				# the longer it's been without a change, the longer we should wait
				curr_wait = time.time() - last_change_time
				sleep_time = max(min(math.log(curr_wait / 2), max_wait_time), min_wait_time)
				print("waiting for {} seconds".format(sleep_time))
				time.sleep(sleep_time)
		else:
			send_color(color, sock)

def send_color(color, sock):
	tosend = str.encode(".".join(map(str, color)), 'utf-8')
	sock.send(tosend)
	print(color)

def img_avg(img):
	# Modified version of the algorithm from https://github.com/kershner/screenBloom
	low_threshold = 10

	img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

	rgb = np.array([0, 0, 0])
	total_pixels = 0

	for pixel in img:
		if pixel[0] > low_threshold and pixel[1] > low_threshold and pixel[2] > low_threshold:
			rgb += pixel
			total_pixels += 1

	rgb /= total_pixels

	# If computed average below darkness threshold, set to the threshold

	for index, item in enumerate(rgb):
		if item <= low_threshold:
			rgb[index] = low_threshold
	
	return (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def row_avg(row):
	low_threshold = 10
	total_pixels = 0
	avg_pixel = np.array([0, 0, 0])
	for pixel in row:
		if pixel[0] > low_threshold and pixel[1] > low_threshold and pixel[2] > low_threshold:
			avg_pixel += pixel
			total_pixels += 1

	return avg_pixel / max(total_pixels, 1)

if __name__ == '__main__':
	main()