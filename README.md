# LEDBacklightPi
Syncs RGB LEDs to the current contents of the desktop using a Raspberry Pi. Uses [ColorThief by Shipeng Feng](https://github.com/fengsp/color-thief-py) and [MMCQ.py](https://github.com/admire93/mmcq.py)

Instructions
------------

Wire up the Pi to the LED strip as shown [here](http://popoklopsi.github.io/RaspberryPi-LedStrip/#!/), then run Pi/main.py on your Raspberry Pi and Windows/main.py on your Windows machine.

Caveats
-------

* Does not work with exclusive fullscreen apps (i.e. games) because of how DirectX works. You'll have to run games in windowed or borderless windowed mode for the screen to be analyzed properly.
* Copy-protected media (e.g. Netflix) appears as a black box and will be analyzed by the color selection algorithm as such. Which makes sense, if you think about it. Non-protected media like YouTube and MPC-HC work perfectly fine.
* On multi-monitor setups, only looks at the primary monitor. This is a limitation of the PIL library.
* Taking a screenshot then analyzing it consumes a surprising amount of CPU resources. As a result, it consumes 100% of one CPU core on your PC and, on my i7-4790K @ 4.6 GHz, only analyzes about 5 frames per second. It looks pretty smooth in reality, but it does consume quite a lot of energy in the process. I may decide to decrease the polling rate based on CPU load or the colors not changing for a long period of time.