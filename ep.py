# ep.py - prints some random data to an ESC POS printer connected via
# USB
#
# Copyright (c) 2017 Cloudflare, Inc.

from escpos.printer import Usb
from datetime import datetime

import random, string, os, qrcode, argparse

# Use the system random number generator (which is os.urandom() which
# will be /dev/urandom).
rnd = random.SystemRandom()

# text outputs string s to printer p accumuating the printed text in
# qrl
def text(p, s):
    qrl.append(s)
    s += "\n"
    p.text(s)

# get_printer returns the printer connected via USB. To use find the
# Product ID and Vendor ID and fill them in here.
def get_printer():
    return Usb(0x067b, 0x2305, 0)

# image prints image f (either a file or an image) to printer p
def image(p, f):
    p.image(f, True, True, "bitImageColumn")

# rand_string returns a random string of length n drawn from alphabet
# a
def rand_string(a, n):
    return "".join(rnd.choice(a) for _ in range(n))

magic8 = ["It is certain", "It is decidedly so", "Without a doubt", "Yes, definitely",
          "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
          "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
          "Better not tell you now", "Cannot predict now", "Concentrate and ask again", 
          "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
          "Very doubtful"]

# define and parse a set of command line options
parser = argparse.ArgumentParser()
parser.add_argument("--mazey", type=bool, action="store_true", default=False,
                    help="Print a mazey receipt, with only a maze and no other random data")
args = parser.parse_args()

qrl = ["Cloudflare"]
p = get_printer()

p.set("center", "a", "b")
image(p, "logo.png")
text(p, "FREE RANDOMNESS")
text(p, "FROM LAVA LAMPS")
text(p, "& OTHER SOURCES")

if not args.mazey:
    p.set("center")
    text(p, "\nRANDOM NUMBER < 1,000,000")
    text(p, str(rnd.randint(0, 999999)))

    # The diceware output requires the diceware program (pip install
    # diceware) That program uses random.SystemRandom by default
    text(p, "\nSIX WORD DICEWARE PASSWORD")
    dice = os.popen("diceware -d' '").read()
    qrl.append(dice)
    p.block_text(dice, 32)
    text(p, "")

    text(p, "\n128-BIT ENTROPY PASSWORDS")
    text(p, rand_string("0123456789ABCDEF", 32))
    text(p, rand_string(string.letters+string.digits, 22))
    text(p, rand_string(string.letters+string.digits+string.punctuation, 20))

    text(p, "\nMAGIC 8 BALL SAYS")
    text(p, rnd.choice(magic8))

    text(p, "\nSCAN ME")
    qr = qrcode.QRCode(version=None, box_size=4, border=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qrl.append("cloudflare.com")
    qr.add_data("\n".join(qrl))
    qr.make(fit=True)
    img = qr.make_image()
    image(p, img._img.convert("RGB"))

text(p, "\nRANDOM PUZZLES")
os.system("python mazes.py --prims -s 30 30")
image(p, "maze.png")
if not args.mazey:
    os.system("python sudoku.py")
    image(p, "sudoku.png")

dt = datetime.utcnow()
text(p, "\n" + dt.isoformat("Z"))
text(p, "cloudflare.com")

p.cut()
