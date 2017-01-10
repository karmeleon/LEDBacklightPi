from extractors.base_extractor import BaseExtractor
import pyopencl as cl
import math

class BaseCLExtractor(BaseExtractor):
	"""Base class for extractors using OpenCL.
	
	Extends:
		BaseExtractor
	"""

	# Override this in subclasses.
	CL_SOURCE = "//CL//"

	def __init__(self):
		# having both platforms and devices is stupid, I hate this
		# Just choose the first GPU you come across
		chosen_device = None
		for platform in cl.get_platforms():
			if not chosen_device:
				for device in platform.get_devices(device_type=cl.device_type.GPU):
					chosen_device = device
					break

		if not chosen_device:
			print('No GPU found, use a different algorithm')
			return

		print('Init\'ing OpenCL with device {}'.format(chosen_device.name))
		# this may not work too well on devices with non-square max_work_group_size
		max_work_group_dim_size = int(math.sqrt(chosen_device.max_work_group_size))
		self.max_work_item_sizes = (max_work_group_dim_size, max_work_group_dim_size)

		self.ctx = cl.Context(devices=[chosen_device])
		self.queue = cl.CommandQueue(self.ctx)
		self.prg = cl.Program(self.ctx, self.CL_SOURCE).build()