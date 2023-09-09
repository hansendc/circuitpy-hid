# SPDX-License-Identifier: GPL-2.0
# Copyright 2023, Dave Hansen <dave@sr71.net>

from digitalio import *
from touchio import *
from board import *
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

# Built in red LED
led = DigitalInOut(D13)
led.direction = Direction.OUTPUT

# Capacitive touch on A0
touch = TouchIn(A0)

mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

global iPhone
global iPad
global passcode
global inch
global cm
global up
global down
global left
global right
global sleep_between_move
global max_per_move
max_per_move = 12

up    = -1.0
down  =  1.0
left  = -1.0
right =  1.0

iPad = False
iPhone = not iPad

def cat_file(f):
        try:
                with open(f, "r") as fp:
                        content = fp.read()
                        fp.close()
                        return content
        except OSError as e: # Typically when the filesystem isn't writeable...
                return None

def delay(seconds):
	time.sleep(seconds)
	return

def dev_setup():
	global inch
	global cm
	global sleep_between_move
	if iPad:
		cm = 64
		sleep_between_move = 0.050
	# scale down for the iPhone 8:
	if iPhone:
		cm = 76
		sleep_between_move = 0.004
	inch = int(cm * 2.54)

def move_piece(xy):
	this_xy = min(abs(xy), max_per_move)
	if (xy < 0):
		#print("inverted xy", this_xy)
		this_xy = -this_xy

	return this_xy

def should_run():
	return not touch.value

def mouse_move(x, y):
	print("trying to move by %d,%d" % (x, y))
	while (x != 0) or (y != 0):
		this_x = move_piece(x)
		this_y = move_piece(y)

		x = x - this_x
		y = y - this_y
		print("x = %d, this_x = %d, y = %d, this_y = %d" % (x, this_x, y, this_y))
		mouse.move(int(this_x), int(this_y), 0)
		delay(0.050)
		if not should_run():
			break

def pogo_reset_iPad():
	global inch
	global cm
	# Roughly the dimensions of the whole iPad down and left:
	mouse_move(-18 * cm, 25 * cm);

	# move away from the menu popup:
	mouse_move( 3 * inch, -3 * inch);
	delay(1)
	mouse_move(-3 * inch,  3 * inch);

def pogo_reset_iPhone():
	global cm
	# Roughly the dimensions of the whole iPhone down and left:
	# HACK! The iPhone 14 has a curved edge. If the 'y' move
	# here is more extreme than 'x', the 'x' will finish first
	# and then will be left finishing 'y' by moving straight
	# down. This "slides" down the curved edge of the screen,
	# moving the cursor to the right and screwing this up.
	#
	# Give this more 'x' movement. That slides the cursor
	# to be more consistent with the more rectanguar screens.
	mouse_move(-15 * cm, 14 * cm);

	# No menu bar popup on the iPhone

def pogo_reset():
	if iPhone:
		pogo_reset_iPhone()
	if iPad:
		pogo_reset_iPad()

#// 100 for a move_interval seeems to work but is pretty slow
#// 50 seems to be a lot faster but is probably close to tripping the accleration triggers
move_interval = 50

def key_delay():
	delay(0.5)

def kb_press(keys):
	for k in keys:
		keyboard.press(k)
		delay(0.1)
	keyboard.release_all()
	key_delay()

def send_letters(letters):
	##print("sending '%s'" % (letters))
	##return #fixme
	for l in letters:
		kb_press([Keycode.A + ord(l) - ord('a')])

def send_numbers(numbers):
	##print("sending '%s'" % (numbers))
	##return #fixme
	for n in numbers:
		kb_press([Keycode.ONE + ord(n) - ord('1')])

def repeat_key(key, nr):
	##return #fixme
	for i in range(nr):
		kb_press([key])

def wake_up_type_passcode():
	repeat_key(Keycode.ESCAPE, 20)
	send_numbers(passcode)

def open_pgo():
	print("open_pgo()")
	kb_press([ Keycode.GUI, Keycode.H])
	delay(4)

	kb_press([ Keycode.GUI, Keycode.SPACE ])
	delay(4)
	send_letters("pokemo")
	delay(10)
	kb_press([Keycode.ENTER])
	delay(10)

def drag_left():
	mouse.press(Mouse.LEFT_BUTTON)
	delay(0.5)
	mouse_move(1.0*inch*left,  0.0*inch*up)
	mouse.release(Mouse.LEFT_BUTTON)
	mouse_move(1.0*inch*right, 0.0*inch*up)

def open_gift():
	# Click the gift itself:
	mouse.click(Mouse.LEFT_BUTTON)
	delay(2)

	# Move over and click the pin:
	mouse_move(1.0*inch*right, 0.0*inch*up)
	mouse.click(Mouse.LEFT_BUTTON)
	delay(3)
	mouse.click(Mouse.LEFT_BUTTON)
	delay(1)
	mouse_move(1.0*inch*left, 0.0*inch*up)

	# Click the "Open" button:
	mouse.click(Mouse.LEFT_BUTTON)
	# Wait for the gunk to open:
	delay(15)

def send_gift():
	# Move 0.5x0.5 in and click "Send Gift"
	mouse_move(0.5*inch*right, 0.5*inch*up)
	mouse.click(Mouse.LEFT_BUTTON)
	delay(1)

	# Move 0.0x2.0 in and click on gift
	mouse_move(0.0*inch, 2.0*inch*up)
	mouse.click(Mouse.LEFT_BUTTON)
	delay(1)

	# right 0.25", and back down 1.75" click "Send"
	mouse_move(0.25*inch*right, 1.75*inch*down)
	mouse.click(Mouse.LEFT_BUTTON)
	delay(5)

	drag_left()
	delay(2)
	# a light reset:
	mouse_move(2*inch*left, 2.0*inch*down)
	delay(2)

print("going...")
passcode = cat_file("passcode.txt")
dev_setup()
print("passcode: '%s'" % (passcode))
while True:
	print("touch.value: '%s'" % ( touch.value))
	if not should_run():
		print("not doing anything")
		delay(1)
		continue
	if False:
		wake_up_type_passcode()
		delay(2)
		open_pgo()

		delay(2)
	pogo_reset()
	for i in range(20):
		break
		send_gift()

	for i in range(20):
		mouse_move(1.0*inch*right, 0.8*inch*up)
		open_gift()
		drag_left()
		# Mini reset:
		mouse_move(1.5*inch*left , 1.2*inch*down)

	break
