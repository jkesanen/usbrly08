# usbrly08

A Python library and tool for controlling Robot Electronics/Devantech USB-RLY08-B eight relay output board. Tested on Python 2.7 and 3.6.

In addition to USBRLY08-B, usbrly08.py should also work with following models, as the control commands are the same (not tested by the author):

* USBRLY02
* USBRLY08
* USBRLY16
* USBRLY16L

## Usage example as a library

```
Python 3.6.2 (default, Oct  1 2017, 03:29:14)
[GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import serial
>>> s = serial.Serial("/dev/tty.usbmodem00030611")
>>> import usbrly08
>>> u = usbrly08.usbrly(s)
>>> u.get_serial()
'00030612'
>>> u.set_states(0xff)
>>> u.set_all(False)
>>> u.get_sw_version()
(8, 2)
```

## Usage example as a command line tool

```
% ./usbrly08.py -p /dev/tty.usbmodem00030611 -g -a off
0x00
0 off
1 off
2 off
3 off
4 off
5 off
6 off
7 off
```

Use command line parameter `--help` for usage.

## Limitation

On one Macbook I've noticed using many `-n` switches doesn't always work reliably. If parameters `-n 0 -n 1 -n 2 -n 3 -n 4 -n 5 -n 6 -n 7` are specified, sometimes all relays aren't enabled. It might be related to timing, that the module is not able to receive many commands in series. Adding 1 ms delay (time.sleep(0.001)) between the sets fixed the issue. On Windows computers this hasn't reproduced.

## Notice

The author of this code is not associated with the company manufacturing and selling the hardware. This code has been developed to fulfill the personal needs of the author. If you have hardware related questions, please contact the manufacturer.

## License

The 3-Clause BSD License
