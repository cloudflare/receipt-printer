Cloudflare Randomness Printer
-----------------------------

The Cloudflare Randomness Printer prints on demand a 'receipt'
containing the following:

1. A random number less than 1,000,000

2. A six word [diceware](https://en.wikipedia.org/wiki/Diceware) password

3. Three passwords that have 128-bits of entropy. One has just
hexadecimal digits, one has alphanumerics and another printable ASCII.

4. A random response from the [Magic 8 Ball](https://en.wikipedia.org/wiki/Magic_8-Ball).

5. A QR code containing the information from 1 to 4.

6. A maze generated using [Prim's
Algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm) using a
modified version of [this
code](http://www.brian-gordon.name/portfolio/maze.html) to make it
more legible on the printer.

7. A random Sudoku generated using a modified version of [this
code](http://davidbau.com/downloads/sudoku.py).

8. The current UTC date and time in ISO8601 format.

![](https://github.com/cloudflare/receipt-printer/raw/master/printing.gif)

The Printer
-----------

The specific printer used is a [GSAN
5870W](http://www.gsan.cn/En/prodShow.asp?vid=144) Thermal Receipt
Printer but the code will work with other printers that handle the
[ESC/POS](https://en.wikipedia.org/wiki/ESC/P) format (which is very
common). This specific printer was only used because we had one lying
around.

![](https://github.com/cloudflare/receipt-printer/raw/master/output.jpg)

Random Source
-------------

The program uses /dev/urandom which is fed with entropy from
Cloudflare's internal randomness source (such as [lava
lamps](https://twitter.com/swiftonsecurity/status/728603357665857537?lang=en))

Button
------

The code above runs on a Raspberry Pi Model B with an
[LED](https://thepihut.com/blogs/raspberry-pi-tutorials/27968772-turning-on-an-led-with-your-raspberry-pis-gpio-pins)
and a [button](http://razzpisampler.oreilly.com/ch07.html) connected
to two GPIO ports. Pressing the button simply executes `ep.py`. It
uses code similar to this:

```python
import RPi.GPIO as GPIO
import time, os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.OUT)

while True:
    input_state = GPIO.input(18)
    if input_state == False:
        GPIO.output(25, GPIO.HIGH)
        os.system("python ep.py")
        GPIO.output(25, GPIO.HIGH)
    time.sleep(0.01)
```

The button is connected between GND and GPIO18. The LED is connected
between GND and GPIO25 with a 330 Ohm resistor to GND.

![](https://github.com/cloudflare/receipt-printer/raw/master/button.jpg)
