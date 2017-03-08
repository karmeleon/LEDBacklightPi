import time, socket, math, struct
import PIL.ImageGrab as ig
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
from functools import partial

from extractors.mean_extractor import MeanExtractor
from extractors.cl_mean_extractor import CLMeanExtractor
from extractors.colorthief_extractor import ColorThiefExtractor
from extractors.hsv_extractor import HSVExtractor
from extractors.cl_hsv_extractor import CLHSVExtractor

import numpy as np


class LEDBacklightPiClient(object):
	ALGORITHMS = {
		'MEAN': MeanExtractor,			# ~64ms
		'MEAN_CL': CLMeanExtractor,		# ~30ms
		'FANCY': ColorThiefExtractor,	# ~230ms
		'HSV': HSVExtractor,			# ~350ms
		'HSV_CL': CLHSVExtractor,		# ~50ms
	}

	CHOSEN_ALGORITHM = ALGORITHMS['HSV_CL']
	SHOW_TIMING = False

	def __init__(self):
		self.extractor = self.CHOSEN_ALGORITHM()

	def main(self):
		# static DHCP allocation of RPi
		address = input("IP address of Raspberry Pi? (192.168.1.120) ")
		if address == "":
			address = "192.168.1.120"

		sock = socket.socket()
		port = 1420

		sock.connect((address, port))

		
		last_color = LabColor(0.0, 0.0, 0.0)
		delta_e_threshold = 5.0
		max_wait_time = 1.0		# seconds
		min_wait_time = 0.05	# seconds
		last_change_time = time.time()
		
		refresh_rate = 0.1

		allow_throttling = True

		while True:
			try:
				image = ig.grab()
			except Exception:
				# thrown for unknown reasons
				print("Screen grab failed for some reason, it's probably fine.")
				time.sleep(5)
				continue
			
			last_image_time = time.time()
			w, h = image.size
			start = time.time()
			color = self.extractor.get_color(image)
			end = time.time()
			if self.SHOW_TIMING:
				print(end - start)

			if allow_throttling:
				# find dE from previous color
				srgb_color = sRGBColor(*color, is_upscaled=True)
				# convert to LAB color
				lab_color = convert_color(srgb_color, LabColor, target_illuminant='d50')
				# get dE
				delta_e = delta_e_cie2000(lab_color, last_color)

				# send the color
				self.send_color(color, sock)

				# if the color change is above the threshold, reset the clock
				if delta_e >= delta_e_threshold:
					last_color = lab_color
					last_change_time = time.time()
				else:
					# otherwise wait a bit before looking again based off how long it's been since a change
					# the longer it's been without a change, the longer we should wait
					curr_wait = time.time() - last_change_time
					sleep_time = max(min(math.log(curr_wait / 2), max_wait_time), min_wait_time)

					time.sleep(sleep_time)

			else:
				self.send_color(color, sock)
				wait_time = max(0.0, refresh_rate - (time.time() - last_image_time))
				time.sleep(wait_time)

	def send_color(self, color, sock):
		color = self.clamp_color_to_byte(color)
		tosend = struct.pack('BBB', *color)
		sock.send(tosend)

	def clamp_color_to_byte(self, color):
		return (self.clamp_to_byte(color[0]), self.clamp_to_byte(color[1]), self.clamp_to_byte(color[2]))

	def clamp_to_byte(self, i):
		# http://stackoverflow.com/a/4092677
		return sorted((0, 255, i))[1]

if __name__ == '__main__':
	LEDBacklightPiClient().main()