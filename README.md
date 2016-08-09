# LEDBacklightPi
Syncs RGB LEDs to the current contents of the desktop using a Raspberry Pi. Uses a modified version of img_avg from [ScreeonBloom](https://github.com/kershner/screenBloom) and [fengsp's color-thief-py](https://github.com/fengsp/color-thief-py).

Requirements
------------

* Python 3.X
* Pillow installed on the host PC


Instructions
------------

Wire up the Pi to the LED strip as shown [here](http://popoklopsi.github.io/RaspberryPi-LedStrip/#!/), then run Pi/main.py on your Raspberry Pi and Windows/main.py on your Windows machine.

Caveats
-------

* Does not work with exclusive fullscreen apps (i.e. games) because of how DirectX works. You'll have to run games in windowed or borderless windowed mode for the screen to be analyzed properly.
* Copy-protected video (e.g. Netflix) appears as a black box and will be analyzed by the color selection algorithm as such. Which makes sense, if you think about it. Non-protected media like YouTube and MPC-HC work perfectly fine.
* On multi-monitor setups, the program only looks at the primary monitor. This is intentional; it's intended to mirror the colors of your game or video, not your secondary screen.
* Taking and analyzing a screenshot 10 times per second is surprisingly CPU-intensive. This app will cause your CPU to idle a bit warmer than you're used to. I'm working on refining the algorithms to minimize the power usage, but for right now the difference is noticeable.