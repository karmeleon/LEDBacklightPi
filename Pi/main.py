import socket
import pigpio
import select
import threading

def main():
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(("192.168.1.120", 1420))
	serversocket.listen(5)

	gpio = pigpio.pi()

	while True:
		clientsocket, address = serversocket.accept()
		print(str.format("Client connected from {}", address))
		t = threading.Thread(target=manage_connection, args=(clientsocket, gpio))
		t.daemon = True
		t.start()

def manage_connection(socket, gpio):
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
				#print(str.format("R:{}, G:{}, B:{}", color[0], color[1], color[2]))
				set_color(color, gpio)

def set_color(color, gpio):
	# R:17, G:22, B:24
	gpio.set_PWM_dutycycle(17, color[0])
	gpio.set_PWM_dutycycle(22, color[1])
	gpio.set_PWM_dutycycle(24, color[2])


if __name__ == '__main__':
	main()
