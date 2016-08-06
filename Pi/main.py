import socket, select, threading, queue, struct
import pigpio
import led_thread

def main():
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(("192.168.1.120", 1420))
	serversocket.listen(5)

	color_q = queue.Queue()

	color_thread = led_thread.LEDThread(color_q)
	color_thread.setDaemon(True)
	color_thread.start()

	while True:
		clientsocket, address = serversocket.accept()
		print(str.format("Client connected from {}", address))
		t = threading.Thread(target=manage_connection, args=(clientsocket, color_q))
		t.daemon = True
		t.start()

def manage_connection(socket, color_q):
	while True:
		buf = bytearray()
		while len(buf) < 3:
			buf += socket.recv(3 - len(buf))
			if len(buf) == 0:
				print("Socket closed, ending thread")
				return
		color = struct.unpack('BBB', buf)

		# send the new color to the color thread
		color_q.put(color)

if __name__ == '__main__':
	main()