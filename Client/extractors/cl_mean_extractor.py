from extractors.base_cl_extractor import BaseCLExtractor
import pyopencl as cl
import numpy as np
import math

class CLMeanExtractor(BaseCLExtractor):
	"""Extractor that uses OpenCL to run a crude color-mean extraction method.
	Very perfomant, but gives the same shitty results as MeanExtractor.
	
	Extends:
		BaseCLExtractor
	"""

	# fraction of pixels per side to analyze
	SCALE_FACTOR = 1/10

	CL_SOURCE = '''//CL//

	#pragma OPENCL EXTENSION cl_khr_local_int32_base_atomics : enable

	__kernel void get_color(
		read_only image2d_t img,
		__global uint *output,
		const uint width,
		const uint height
	) {
		const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;
		float2 pos = (float2)(get_global_id(0), get_global_id(1)) / (float2)(height, width);
		int group = get_group_id(0) + get_num_groups(0) * get_group_id(1);

		__constant float4 low_threshold = (float4)(10.0/255, 10.0/255, 10.0/255, 255.0/255);
		__constant float4 high_threshold = (float4)(245.0/255, 245.0/255, 245.0/255, 0);

		__local uint color_total[3];
		// no memset()? really?
		color_total[0] = 0;
		color_total[1] = 0;
		color_total[2] = 0;
		__local uint pixel_count;
		pixel_count = 0;

		if(pos[0] < height && pos[1] < width) {
			float4 pixel = read_imagef(img, sampler, pos);
			if(any(isgreater(pixel, low_threshold)) && any(isless(pixel, high_threshold))) {
				atom_inc(&pixel_count);
				atom_add(&color_total[0], (int)(pixel.x * 255));
				atom_add(&color_total[1], (int)(pixel.y * 255));
				atom_add(&color_total[2], (int)(pixel.z * 255));
			}
		}

		barrier(CLK_LOCAL_MEM_FENCE);
		if(get_local_id(0) == 0 && get_local_id(1) == 0) {
			output[group * 4] = color_total[0];
			output[group * 4 + 1] = color_total[1];
			output[group * 4 + 2] = color_total[2];
			output[group * 4 + 3] = pixel_count;
		}
	}
	'''


	def get_color(self, img):
		# OpenCL only supports RGBA images, not RGB, so add an alpha channel
		src = np.array(img.convert('RGBA'))
		src.shape = w, h, _ = img.width, img.height, 4

		w = int(w * self.SCALE_FACTOR)
		h = int(h * self.SCALE_FACTOR)

		local_size = self.max_work_item_sizes
		global_size = (math.ceil(h / local_size[0]), math.ceil(w / local_size[1]))

		total_work_groups = global_size[0] * global_size[1]

		mf = cl.mem_flags
		src_buf = cl.image_from_array(self.ctx, src, 4, norm_int=True)

		out = np.zeros(4 * total_work_groups, dtype=np.int32)
		out_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, size=out.itemsize * 4 * total_work_groups)

		kernel = self.prg.get_color
		kernel.set_scalar_arg_dtypes([None, None, np.uint32, np.uint32])
		kernel(self.queue, global_size, local_size, src_buf, out_buf, w, h, g_times_l=True)

		cl.enqueue_copy(self.queue, dest=out, src=out_buf, is_blocking=True)

		# this sum takes .1 ms at 3440x1440, don't even bother OpenCL-ifying it
		resized_out = np.reshape(out, (out.shape[0] / 4, 4))
		summed_out = np.sum(resized_out, axis=0)

		avg_out = (summed_out / summed_out[3])[:3].astype(int)

		return avg_out