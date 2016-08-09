import threading, queue, time, colorsys
import pigpio

class LEDThread(threading.Thread):
	def __init__(self, color_q):
		super(LEDThread, self).__init__()

		self.color_q = color_q
		self.last_color = (0, 0, 255)
		self.current_color = (0, 0, 255)
		self.next_color = (0, 0, 255)
		# last_time is the time at which last_color was received
		self.last_time = time.time()
		self.duration = 0.1
		self.max_duration = 1.0

		self.saturation_factor = 1.0

		self.gpio = pigpio.pi()

	def run(self):
		print("LEDThread now running")
		while True:
			curr_time = time.time()
			# constantly loop and fade colors
			# see if there's a new color
			try:
				color = self.color_q.get(False)

				# there's a new color, so set the current color as the last color
				# and this new color as the next color
				# convert RGB to HSV, saturate it a little more, then back to RGB
				color = self.int_tuple_to_float(color)
				hsv = colorsys.rgb_to_hsv(*color)
				saturated_color = (hsv[0], min(hsv[1] * self.saturation_factor, 1.0), hsv[2])
				saturated_color = colorsys.hsv_to_rgb(*saturated_color)
				#saturated_color = colorsys.hsv_to_rgb(*hsv)
				color = self.float_tuple_to_int(saturated_color)

				self.change_color(color, min(curr_time - self.last_time, self.max_duration))
			except queue.Empty:
				# no new color in the queue
				# if it's been 5 seconds since the last color, fade to black
				if curr_time - self.last_time > 5.0:
					self.change_color((0, 0, 0), 1.0)

			# now start/continue the fade
			fade_pct = min((curr_time - self.last_time) / self.duration, 1.0)
			interpolated_color = self.interpolate_color(fade_pct)
			self.current_color = interpolated_color
			self.set_color(interpolated_color)

			# #notcinematic
			time.sleep(.016)

	def change_color(self, color, duration):
		self.last_color = self.current_color
		self.next_color = color
		self.duration = duration
		self.last_time = time.time()

	def float_tuple_to_int(self, tuple):
		return (int(tuple[0] * 255), int(tuple[1] * 255), int(tuple[2] * 255))

	def int_tuple_to_float(self, tuple):
		return (tuple[0] / 255.0, tuple[1] / 255.0, tuple[2] / 255.0)

	def interpolate_color(self, fade_pct):
		# numpy would be nice here, but I don't want to require a huge library
		# for just one usage.
		r = int(self.next_color[0] * fade_pct + self.last_color[0] * (1.0 - fade_pct))
		g = int(self.next_color[1] * fade_pct + self.last_color[1] * (1.0 - fade_pct))
		b = int(self.next_color[2] * fade_pct + self.last_color[2] * (1.0 - fade_pct))

		return (r, g, b)

	def set_color(self, color):
		# R:17, G:22, B:24
		try:
			self.gpio.set_PWM_dutycycle(17, self.clamp_to_byte(color[0]))
			self.gpio.set_PWM_dutycycle(22, self.clamp_to_byte(color[1]))
			self.gpio.set_PWM_dutycycle(24, self.clamp_to_byte(color[2]))
		except Exeption:
			print(color)

	def clamp_to_byte(self, i):
		# http://stackoverflow.com/a/4092677
		return sorted((0, 255, i))[1]