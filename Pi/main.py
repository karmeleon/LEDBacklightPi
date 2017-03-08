import threading, queue
import pigpio
from led_thread import LEDThread
from bytestream_color_source_thread import BytestreamColorSourceThread
from web_color_source_thread import WebColorSourceThread
from functools import partial

import daemon

class LEDBacklightPiServer(object):
	"""Main server class for LEDBacklightPi"""
	def __init__(self):
		self.accepting_dynamic_color = True

		self.color_q = queue.Queue()
		self.fade_timer = None

		color_thread = LEDThread(self.color_q)
		color_thread.daemon = True
		color_thread.start()

		bytestream_thread = BytestreamColorSourceThread(self.handle_color)
		bytestream_thread.daemon = False
		bytestream_thread.start()

		web_thread = WebColorSourceThread(self.handle_color, self.set_accepting_dynamic_color)
		web_thread.daemon = False
		web_thread.start()

		self.handle_color(False, (0, 0, 255))

	def set_fade_out_timer(self):
		# stop the previous timer, if any
		if self.fade_timer:
			self.fade_timer.cancel()
		# then start a new one
		fade_partial = partial(self.handle_color, True, (0, 0, 0))
		self.fade_timer = threading.Timer(5, fade_partial)
		self.fade_timer.start()

	def cancel_fade_out_timer(self):
		if self.fade_timer:
			self.fade_timer.cancel()

	def set_accepting_dynamic_color(self, accepting):
		"""Method to allow other threads to set the dynamic color accepting status
		:param accepting: Boolean to set self.accepting_dynamic_color to
		"""
		if accepting:
			# set a timer to fade out colors
			self.set_fade_out_timer()
		else:
			# cancel existing fade timers
			self.cancel_fade_out_timer()
		self.accepting_dynamic_color = accepting

	def handle_color(self, is_static_color, color):
		"""Callback for setting colors from other threads

		:param is_static_color: True if this color should continue until some other
			color somes in, False if the standard 5 second timeout shoudl apply
		:param color: tuple of (r,g,b) incoming color
		"""
		if not is_static_color and self.accepting_dynamic_color:
			# add this color to the queue, but schedule adding black (i.e.
			# turning the light off) after 5s
			self.color_q.put(color)
			self.set_fade_out_timer()
		elif is_static_color:
			# cancel the fade timer so it doesn't override the new static color
			self.color_q.put(color)
			self.cancel_fade_out_timer()

with daemon.DaemonContext():
	LEDBacklightPiServer()
