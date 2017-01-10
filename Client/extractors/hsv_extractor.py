from extractors.base_extractor import BaseExtractor
import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, HSVColor

class HSVExtractor(BaseExtractor):
	"""An extractor that uses the HSV color space to find the dominant color.
	Very slow, but gives good results, is relatively stable in slow-moving
	scenes, and is embarrasingly parallel (see CLHSVExtractor!)
	
	Extends:
		BaseExtractor
	"""

	def get_color(self, img):
		self.downsample_img(img, 20)
		# flatten into a 1D array of float pixels
		img = np.array(img).reshape(-1, 3).astype(np.float32)

		# number of buckets to put hues in
		h_resolution = 36
		buckets = [[] for i in range(h_resolution)]
		grayscale_bucket = []

		# convert the whole array to hsv
		for idx, pixel in enumerate(img):
			srgb = sRGBColor(*pixel, is_upscaled=True)
			# convert to HSV color
			hsv = convert_color(srgb, HSVColor, target_illuminant='d50')
			img[idx] = hsv.get_value_tuple()
			
			# then bucket it

			# decide if the color is "gray-ish"
			if hsv.hsv_s < 0.2 or hsv.hsv_v < 0.2:
				grayscale_bucket.append(idx)
			# otherwise, stick it in a bucket corresponding to its hue
			else:
				bucket = int(hsv.hsv_h / (360 / h_resolution))
				buckets[bucket].append(idx)

		counts = [len(b) for b in buckets]

		max_count = max(counts)
		max_bucket = counts.index(max_count)

		# if most of the screen is a shade of gray, ignore colors
		if len(grayscale_bucket) > img.shape[0] * 0.8:
			return self.avg_color_by_idx(img, grayscale_bucket)

		# return the mean color of the max bucket and the two adjacent buckets
		#selected_buckets = [(max_bucket - 1) % h_resolution, max_bucket, (max_bucket + 1) % h_resolution]
		#avgs = map(partial(avg_color_by_idx, img), selected_buckets)
		return self.avg_color_by_idx(img, buckets[max_bucket])


	def avg_color_by_idx(self, img, idxs):
		# assumes img is in HSV format, returns RGB format
		h, s, v = 0.0, 0.0, 0.0
		for idx in idxs:
			h += img[idx][0]
			s += img[idx][1]
			v += img[idx][2]
		hsv = HSVColor(h / len(idxs), s / len(idxs), v / len(idxs))
		return convert_color(hsv, sRGBColor).get_upscaled_value_tuple()