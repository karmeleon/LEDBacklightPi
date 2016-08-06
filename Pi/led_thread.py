import threading, queue, time
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
				self.last_color = self.current_color
				self.next_color = color
				# and update the timers
				self.duration = curr_time - self.last_time
				self.last_time = curr_time
			except queue.Empty:
				# no new color in the queue, ignore it
				pass

			# now start/continue the fade
			fade_pct = min((curr_time - self.last_time) / self.duration, 1.0)
			interpolated_color = self.interpolate_color(fade_pct)
			self.current_color = interpolated_color
			self.set_color(interpolated_color)

			# #notcinematic
			time.sleep(.016)

	def interpolate_color(self, fade_pct):
		# numpy would be nice here, but I don't want to require a huge library
		# for just one usage.
		r = int(self.next_color[0] * fade_pct + self.last_color[0] * (1.0 - fade_pct))
		g = int(self.next_color[1] * fade_pct + self.last_color[1] * (1.0 - fade_pct))
		b = int(self.next_color[2] * fade_pct + self.last_color[2] * (1.0 - fade_pct))

		return (r, g, b)

	def set_color(self, color):
		# R:17, G:22, B:24
		self.gpio.set_PWM_dutycycle(17, color[0])
		self.gpio.set_PWM_dutycycle(22, color[1])
		self.gpio.set_PWM_dutycycle(24, color[2])