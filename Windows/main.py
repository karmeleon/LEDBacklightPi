import PIL.ImageGrab as ig
import mmcq
import time
import timeit
import socket
from colorthief import ColorThief

def main():
	# static DHCP allocation of RPi
	address = "192.168.1.120"

	sock = socket.socket()
	port = 1420

	sock.connect((address, port))

	"""
	width = 2000
	images = []
	for i in range(1, math.ceil(1920/width)):
		for j in range(1, math.ceil(1080/width)):
			x1 = i * width
			x2 = min(1920 - 1, i * (width + 1))
			y1 = j * width
			y2 = min(1080 - 1, j * (width + 1))
			print(x1, y1, x2, y2)
			images.append(ig.grab(bbox=(x1, y1, x2, y2)))
	"""

	#print(timeit.timeit('get_dominant_color(1)', "from __main__ import get_dominant_color", number=10) / 10)

	while True:
		#time.sleep(1)
		color = get_dominant_color()
		tosend = str.encode(".".join(map(str, color)), 'utf-8')
		print(tosend)
		sock.send(tosend)


def get_dominant_color(algorithm=0):
	
	image = ig.grab()
	w, h = image.size
	image.thumbnail((int(w / 5), int(h / 5)))
	
	if algorithm == 0:
		return mmcq.get_dominant_color(image)
	elif algorithm == 1:
		ct = ColorThief(image)
		return ct.get_color(quality=1)

if __name__ == '__main__':
	main()