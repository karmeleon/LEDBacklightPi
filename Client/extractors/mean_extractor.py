from extractors.base_extractor import BaseExtractor
import numpy as np

class MeanExtractor(BaseExtractor):
	"""An extractor that takes the mean of the image, more or less.
	Very performant, but not very good at finding the right color.
	Usually returns some shade of gray. If you have a GPU at all,
	you should be using CLMeanExtractor instead.
	
	Extends:
		BaseExtractor
	"""

	def get_color(self, img):
		self.downsample_img(img, 20)
		# Modified version of the algorithm from https://github.com/kershner/screenBloom
		img = np.array(img)
		low_threshold = 10
		high_threshold = 245

		img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

		rgb = np.array([0, 0, 0])
		total_pixels = 0

		for pixel in img:
			# don't count pixels that are too dark or too light
			# surprisingly, the numpy approach is slower than the raw Python approach by ~10ms
			# too bad it's uglier. oh well.
			#if np.any(np.greater(pixel, low_threshold)) and np.any(np.less(pixel, high_threshold)):

			if pixel[0] > low_threshold or pixel[1] > low_threshold or pixel[2] > low_threshold:
				if pixel[0] < high_threshold or pixel[1] < high_threshold or pixel[2] < high_threshold:
					rgb += pixel
					total_pixels += 1

		if total_pixels > 1:
			rgb /= total_pixels

		# If computed average below darkness threshold, set to the threshold
		"""
		for index, item in enumerate(rgb):
			if item <= low_threshold:
				rgb[index] = low_threshold
		"""
		return (int(rgb[0]), int(rgb[1]), int(rgb[2]))