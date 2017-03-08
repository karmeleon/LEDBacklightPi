from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import parse_qs
from colormath.color_objects import sRGBColor

class WebColorSource(BaseHTTPRequestHandler):
	"""Extremely simple server that allows the user to switch
	between displaying a static color and accepting dynamic
	colors from a remote host.
	
	Extends:
		BaseHTTPRequestHandler
	"""

	WEBPAGE = """
<html>
	<head>
		<title>LED Control Panel</title>
	</head>
	<body>
		<form action="save_settings" method="post">
			<input type="radio" name="group" value="static">Static Color</input>
			<input type="color" name="static_color" value="#0000ff"/>
			<input type="radio" name="group" value="dynamic" checked>Dynamic Color</input>
			<input type="submit" value="Save"/>
		</form>
	</body>
</html>
	"""

	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def send_control_page(self):
		self._set_headers()
		self.wfile.write(bytes(self.WEBPAGE, 'UTF-8'))

	def send_404(self):
		self.send_response(404)
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def do_GET(self):
		if self.path == '/':
			self.send_control_page()
		else:
			self.send_404()

	def do_POST(self):
		self._set_headers()
		data_string = self.rfile.read(int(self.headers['Content-Length']))

		self.send_response(200)
		self.end_headers()

		data = parse_qs(data_string)
		if data[b'group'][0] == b'static':
			# we got a static color
			self.set_accepting_dynamic_color(False)
			# convert e.g. "#0000ff" to "0000FF" for the RGB hex parser
			color_str = data[b'static_color'][0][1:].upper()
			color_obj = sRGBColor.new_from_rgb_hex(color_str)
			color_tuple = color_obj.get_upscaled_value_tuple()
			
			self.color_callback(True, color_tuple)
			print('setting static color to ', color_tuple)
		elif data[b'group'][0] == b'dynamic':
			print('setting color to dynamic')
			# ignore the static color, dynamic it is
			self.set_accepting_dynamic_color(True)
		else:
			print(data)

	def color_callback(self, color_callback):
		print('color_callback wasn\'t overridden!')
