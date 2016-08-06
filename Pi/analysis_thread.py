import threading, time, colorsys, multiprocessing
import numpy as np

# this is outside of the object to avoid implicitly passing a Queue to this function
# implicitly via the self object, which causes a crash
def row_avg(row):
		low_threshold = 10
		total_pixels = 0
		avg_pixel = np.array([0, 0, 0])
		for pixel in row:
			if pixel[0] > low_threshold and pixel[1] > low_threshold and pixel[2] > low_threshold:
				avg_pixel += pixel
				total_pixels += 1

		return avg_pixel / max(total_pixels, 1)

class AnalysisThread(threading.Thread):
	def __init__(self, color_q, okay_q, image_q):
		super(AnalysisThread, self).__init__()

		self.color_q = color_q
		self.okay_q = okay_q
		self.image_q = image_q

	def run(self):
		print("AnalysisThread now running")
		while True:
			# pull a new image from the queue
			image = self.image_q.get()
			# analyze it
			color = self.img_avg(image)
			# send the color to the color thread
			self.color_q.put(color)
			# request another one
			self.okay_q.put(True)

	def img_avg(self, img):
		# Modified version of the algorithm from https://github.com/kershner/screenBloom
		low_threshold = 10

		rgb = 0

		with multiprocessing.Pool(processes=4) as p:
			rows = p.map(row_avg, img)
			rgb = np.mean(rows, axis=0)

		# If computed average below darkness threshold, set to the threshold
		
		for index, item in enumerate(rgb):
			if item <= low_threshold:
				rgb[index] = low_threshold
		
		return (int(rgb[0]), int(rgb[1]), int(rgb[2]))