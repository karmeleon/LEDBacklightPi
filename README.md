# LEDBacklightPi
Syncs RGB LEDs to the current contents of the desktop using a Raspberry Pi. By default it uses a custom OpenCL-based algorithm, but it can optionally use a modified version of img_avg from [ScreeonBloom](https://github.com/kershner/screenBloom), or [fengsp's color-thief-py](https://github.com/fengsp/color-thief-py) instead.

Requirements
------------

* Python 3.x
* Pillow, colormath, pyopencl, and numpy installed on the host PC
* python-daemon installed on the RPi
* An OpenCL-capable GPU and PyOpenCL for the GPU mode
* I've only tested the client program on Windows 10, but there's no reason macOS, Linux, and older versions of Windows shouldn't work.


Instructions
------------

Wire up the Pi to the LED strip as shown [here](http://popoklopsi.github.io/RaspberryPi-LedStrip/#!/), then run python3 main.py start on your Raspberry Pi from the /Pi directory and Client/main.py on your computer.

Caveats
-------

* Does not work with exclusive fullscreen apps (i.e. games) because of how DirectX/OpenGL/Vulkan work. You'll have to run games in windowed or borderless windowed mode for the screen to be analyzed properly.
* Copy-protected video (e.g. Netflix) appears as a black box and will be analyzed by the color selection algorithm as such. Which makes sense, if you think about it. Non-protected media like YouTube and MPC-HC work perfectly fine.
* On multi-monitor setups, the program only looks at the primary monitor. This is intentional; it's intended to mirror the colors of your game or video, not your secondary screen.