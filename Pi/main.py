import socket, select, threading, queue, io, struct
from led_thread import LEDThread
from analysis_thread import AnalysisThread
import numpy as np

def main():
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind(("192.168.1.120", 1420))
	serversocket.listen(5)

	color_q = queue.Queue()
	okay_q = queue.Queue()
	image_q = queue.Queue()

	# put color analysis and PWM control on their own threads
	# so all network communication can be handled in a timely
	# manner on this thread
	led_thread = LEDThread(color_q)
	led_thread.setDaemon(True)
	led_thread.start()

	analysis_thread = AnalysisThread(color_q, okay_q, image_q)
	analysis_thread.setDaemon(True)
	analysis_thread.start()

	while True:
		clientsocket, address = serversocket.accept()
		print(str.format("Client connected from {}", address))
		while True:
			data = receive_data(clientsocket)
			if len(data) == 0:
				print("Socket closed, ending thread")
				break
			else:
				np_img = np.load(io.BytesIO(data))['x']
				# send the new color to the color thread
				image_q.put(np_img)
				# wait for the analysis thread to receive the last frame
				# before retrieving the new frame
				okay_q.get()
				# tell the PC to send a new frame
				clientsocket.send(bytes(b'\xff'))


def receive_data(clientsocket):
	buf = bytearray()
	while len(buf) < 4:
		buf += clientsocket.recv(4)
		# check for closed connection
		if len(buf) == 0:
			return '';
	data_size = struct.unpack('!i', buf[:4])[0]

	data = bytearray()
	total_size = 0
	while total_size < data_size:
		# get a chunk
		buf = clientsocket.recv(min(2048, data_size - total_size))
		# append it to the output buffer
		data += buf
		# increment the counter
		total_size += len(buf)
	return data

if __name__ == '__main__':
	main()
