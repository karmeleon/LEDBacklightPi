from extractors.base_cl_extractor import BaseCLExtractor
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, HSVColor
import pyopencl as cl
import numpy as np
import math, time

class CLHSVExtractor(BaseCLExtractor):
	"""An extractor that uses an OpenCL-accelerated version of my
	HSV color extraction algorithm.

	Extends:
		BaseCLExtractor
	"""
	
	SCALE_FACTOR = 10
	NUM_BUCKETS = 36

	CL_SOURCE = """//CL//

	float4 convert_rgb_to_hsv(float4 rgb) {
		// https://www.cs.rit.edu/~ncs/color/t_convert.html
		float4 hsv = (float4)(1.0f);

		float min = fmin(rgb.x, rgb.y);
		min = fmin(min, rgb.z);

		float max = fmax(rgb.x, rgb.y);
		max = fmax(max, rgb.z);

		hsv.z = max;

		float delta = max - min;

		if(max != 0) {
			hsv.y = delta / max;
		} else {
			// we have black
			return (float4)(0.0f);
		}

		if(rgb.x == max) {
			hsv.x = (rgb.y - rgb.z) / delta;
		} else if(rgb.y == max) {
			hsv.x = 2 + (rgb.z - rgb.x) / delta;
		} else {
			hsv.x = 4 + (rgb.x - rgb.y) / delta;
		}

		// convert to degrees
		hsv.x *= 60;
		if(rgb.x < 0) {
			hsv.x += 360;
		}
		return hsv;
	}

	__kernel void get_color(
		read_only image2d_t src_img,
		__global float* hsv_img,
		const uint width,
		const uint height
	) {
		const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;
		float2 pos = (float2)(get_global_id(0), get_global_id(1)) / (float2)(height, width);

		if(pos[0] < height && pos[1] < width) {
			float4 rgb_pixel = read_imagef(src_img, sampler, pos);

			float4 hsv_pixel = convert_rgb_to_hsv(rgb_pixel);

			int out_idx = (get_global_id(0) + get_global_size(0) * get_global_id(1)) * 3;
			hsv_img[out_idx] = hsv_pixel.x;
			hsv_img[out_idx + 1] = hsv_pixel.y;
			hsv_img[out_idx + 2] = hsv_pixel.z;
		}
	}
	"""

	def get_color(self, img):
		self.downsample_img(img, 5)
		# OpenCL only supports RGBA images, not RGB, so add an alpha channel
		src = np.array(img.convert('RGBA'))
		src.shape = w, h, _ = img.width, img.height, 4

		w = int(w / self.SCALE_FACTOR)
		h = int(h / self.SCALE_FACTOR)

		local_size = self.max_work_item_sizes
		global_size = (math.ceil(h / local_size[0]), math.ceil(w / local_size[1]))

		total_work_groups = global_size[0] * global_size[1]

		mf = cl.mem_flags
		# TODO: only init these once, then reuse them
		src_img = cl.image_from_array(self.ctx, src, 4, norm_int=True)
		hsv_img = cl.Buffer(self.ctx, mf.WRITE_ONLY, size=h * w  * 3 * 4)	# h * w pixels, each with 3 channels of 4 bytes each.

		kernel = self.prg.get_color
		kernel.set_scalar_arg_dtypes([None, None, np.uint32, np.uint32])
		kernel(self.queue, global_size, local_size, src_img, hsv_img, w, h, g_times_l=True)

		out = np.zeros(w * h * 3, dtype=np.float32)
		cl.enqueue_copy(self.queue, dest=out, src=hsv_img, is_blocking=True)
		out = np.reshape(out, (-1, 3))

		# number of buckets to put hues in
		h_resolution = 36
		buckets = [[] for i in range(h_resolution)]
		grayscale_bucket = []
		start = time.time()
		# iterate over the hsv image
		for idx, pixel in enumerate(out):
			# then bucket it
			# decide if the color is "gray-ish"
			if pixel[1] < 0.2 or pixel[2] < 0.2:
				grayscale_bucket.append(idx)
			# otherwise, stick it in a bucket corresponding to its hue
			else:
				bucket = int(pixel[0] / (360 / h_resolution))
				buckets[bucket].append(idx)

		counts = [len(b) for b in buckets]

		max_count = max(counts)
		max_bucket = counts.index(max_count)

		# if most of the screen is a shade of gray, ignore colors
		if len(grayscale_bucket) > out.shape[0] * 0.8:
			return self.avg_color_by_idx(out, grayscale_bucket)

		# return the mean color of the max bucket
		return self.avg_color_by_idx(out, buckets[max_bucket])


	def avg_color_by_idx(self, img, idxs):
		# assumes img is in HSV format, returns RGB format
		h, s, v = 0.0, 0.0, 0.0
		for idx in idxs:
			h += img[idx][0]
			s += img[idx][1]
			v += img[idx][2]
		hsv = HSVColor(h / len(idxs), s / len(idxs), v / len(idxs))
		return convert_color(hsv, sRGBColor).get_upscaled_value_tuple()
