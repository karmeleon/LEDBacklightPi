import threading, queue
from web_color_source import WebColorSource
from socketserver import TCPServer

class WebColorSourceThread(threading.Thread):
	"""A thread that contantly listens for incoming web requests from the dashboard and
	sets the LED colors accordingly.
	"""

	def __init__(self, color_callback, set_accepting_dynamic_color):
		"""
		:param color_callback: a function that will be run with the argument as an (r,g,b)
			tuple when a color comes in from any client
		:param set_accepting_dynamic_color: a function that will be run when the user requests
			dynamic colors to be enabled/disabled from the web dashboard
		"""
		super(WebColorSourceThread, self).__init__()
		# we can't pass arguments into the BaseHTTPRequestHandler subclass, so
		# modify an instance first
		color_source_instance = WebColorSource
		color_source_instance.color_callback = color_callback
		color_source_instance.set_accepting_dynamic_color = set_accepting_dynamic_color
		self.http_server = TCPServer(('0.0.0.0', 1422), color_source_instance)

	def run(self):
		print('HTTP server now running on port 1422')
		self.http_server.serve_forever()
