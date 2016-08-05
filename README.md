# LEDBacklightPi
Syncs RGB LEDs to the current contents of the desktop using a Raspberry Pi. Uses [ColorThief by Shipeng Feng](https://github.com/fengsp/color-thief-py) and [MMCQ.py](https://github.com/admire93/mmcq.py)

Instructions
------------

Wire up the Pi to the LED strip as shown [here](http://popoklopsi.github.io/RaspberryPi-LedStrip/#!/), then run Pi/main.py on your Raspberry Pi and Windows/main.py on your Windows machine.

Caveats
-------

* Does not work with exclusive fullscreen Windows apps (i.e. games) because of how DirectX works. You'll have to run games in windowed or borderless windowed mode for the screen to be analyzed properly.
* On multi-monitor setups, only looks at the primary monitor. This is a limitation of the PIL library.
* Finding the most dominant color of an image is surprisngly compute-intensive. The framerate is not great here. It should be fine for standard desktop work, but the experience will be suboptimal for games and videos. I'll look into rewriting the ColorTheif library in C or something to speed it up.
