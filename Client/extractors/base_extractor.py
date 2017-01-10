class BaseExtractor(object):
	"""Base class for a color extractor, i.e. a routine that extracts
	a dominant color from an image.
	"""

	def downsample_img(self, img, ratio):
		"""Downsamples both dimensions of an image by [ratio] times
		
		Arguments:
			img {PIL image} -- Image to downsample
			ratio {int} -- Number of times to downsample
		"""
		img.thumbnail((int(img.size[0] / ratio), int(img.size[1] / ratio)))

	def get_color(self, img):
		"""Gets the dominant color of an image. Abstract.
		
		Arguments:
			img {PIL image} -- Image to find the color of
		
		Returns:
			{(int, int, int)} -- RGB tuple of dominant color
		"""
		raise NotImplemented