import socket, select, threading, queue
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
	socket.setblocking(0)
	while True:
		# wait up to 30 seconds for data to become available on the socket
		ready = select.select([socket], [], [], 30)
		if ready[0]:
			data = socket.recv(512)
			if len(data) == 0:
				print("Socket closed, ending thread")
				return
			else:
				data = data.decode("utf-8")
				color = [int(s) for s in data.split(sep=".")]

				# send the new color to the color thread
				color_q.put(color)

if __name__ == '__main__':
	main()
