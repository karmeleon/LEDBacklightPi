import threading, queue, socket

class BytestreamColorSourceThread(threading.Thread):
	"""A thread that contantly listens for incoming connections from LEDBacklightPi clients
	and sends the received colors to a listener for display.
	"""

	def __init__(self, color_callback):
		"""
		:param color_callback: a function that will be run with the argument as an (r,g,b)
			tuple when a color comes in from any client
		"""
		super(BytestreamColorSourceThread, self).__init__()
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.bind(("", 1420))
		self.serversocket.listen(5)

	def run(self):
		while True:
			clientsocket, address = self.serversocket.accept()
			print(str.format("Client connected from {}", address))
			t = threading.Thread(target=manage_connection, args=(clientsocket, color_q))
			t.daemon = True
			t.start()

	def manage_connection(socket, color_q, color_callback):
		while True:
			buf = bytearray()
			while len(buf) < 3:
				buf += socket.recv(3 - len(buf))
				if len(buf) == 0:
					print("Socket closed, ending thread")
					return
			color = struct.unpack('BBB', buf)

			# send the new color to the color thread
			color_callback(False, color)