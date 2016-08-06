import time, socket, math
import PIL.ImageGrab as ig
import mmcq
from colorthief import ColorThief
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

def main():
	#print(timeit.timeit('get_dominant_color(2)', 'from __main__ import get_dominant_color', number=50) / 50)
	#return

	# static DHCP allocation of RPi
	address = input("IP address of Raspberry Pi?")
	if address == "":
		address = "192.168.1.120"

	sock = socket.socket()
	port = 1420

	sock.connect((address, port))

	last_color = LabColor(0.0, 0.0, 0.0)
	delta_e_threshold = 5.0
	max_wait_time = 2.0	# seconds
	min_wait_time = 0.033	# seconds
	last_change_time = time.time()

	allow_throttling = True

	while True:
		#time.sleep(1)
		color = get_dominant_color(2)
		if allow_throttling:
			# find dE from previous color
			srgb_color = sRGBColor(*color, is_upscaled=True)
			# convert to LAB color
			lab_color = convert_color(srgb_color, LabColor, target_illuminant='d50')
			# get dE
			delta_e = delta_e_cie2000(lab_color, last_color)

			# if the color change is above the threshold, send the new color and reset the clock
			if delta_e >= delta_e_threshold:
				last_color = lab_color
				last_change_time = time.time()
				send_color(color, sock)
			else:
				# otherwise wait a bit before looking again based off how long it's been since a change
				# the longer it's been without a change, the longer we should wait
				curr_wait = time.time() - last_change_time
				sleep_time = max(min(math.log(curr_wait / 2), max_wait_time), min_wait_time)
				print("waiting for {} seconds".format(sleep_time))
				time.sleep(sleep_time)
		else:
			send_color(color, sock)

		

def send_color(color, sock):
	tosend = str.encode(".".join(map(str, color)), 'utf-8')
	sock.send(tosend)
	print(color)

def get_dominant_color(algorithm=0):
	
	image = ig.grab()
	w, h = image.size
	image.thumbnail((int(w / 5), int(h / 5)))
	
	if algorithm == 0:
		return mmcq.get_dominant_color(image)
	elif algorithm == 1:
		ct = ColorThief(image)
		return ct.get_color(quality=1)
	elif algorithm == 2:
		return img_avg(image)

def img_avg(img):
	# Modified version of the algorithm from https://github.com/kershner/screenBloom
    low_threshold = 10
    mid_threshold = 40
    dark_pixels = 1
    mid_range_pixels = 1
    total_pixels = 1
    r = 1
    g = 1
    b = 1

    # Win version of imgGrab does not contain alpha channel
    if img.mode == 'RGB':
        img.putalpha(0)

    # Create list of pixels
    pixels = list(img.getdata())

    for red, green, blue, alpha in pixels:
        # Don't count pixels that are too dark
        if red < low_threshold and green < low_threshold and blue < low_threshold:
            dark_pixels += 1
        else:
            if red < mid_threshold and green < mid_threshold and blue < mid_threshold:
                mid_range_pixels += 1
            r += red
            g += green
            b += blue
        total_pixels += 1

    n = len(pixels)
    r_avg = r / n
    g_avg = g / n
    b_avg = b / n
    rgb = [r_avg, g_avg, b_avg]

    # If computed average below darkness threshold, set to the threshold
    for index, item in enumerate(rgb):
        if item <= low_threshold:
            rgb[index] = low_threshold

    rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    print(float(dark_pixels) / float(total_pixels) * 100)
    return rgb

if __name__ == '__main__':
	main()