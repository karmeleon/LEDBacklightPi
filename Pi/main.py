import socket
import pigpio

def main():
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind((socket.gethostname(), 1420))
	serversocket.listen(5)
	while True:
		clientsocket, address = serversocket.accept()
		data = receive_data(clientsocket)
		print(data)

def receive_data(clientsocket):
	chunks = []
	bytes_recd = 0
	while bytes_recd < MSGLEN:
		chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return b''.join(chunks)





if __name__ == '__main__':
	main()