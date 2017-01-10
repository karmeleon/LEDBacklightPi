from extractors.base_extractor import BaseExtractor
import extractors.colorthief

class ColorThiefExtractor(BaseExtractor):
	"""An extractor that uses the ColorThief library. Slow and liable to quickly
	flip between colors in barely-moving scenes, but otherwise gives great results.
	
	Extends:
		BaseExtractor
	"""

	def get_color(self, img):
		self.downsample_img(img, 20)
		return colorthief.ColorThief(img).get_color(1)