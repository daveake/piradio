from RPi import GPIO
from time import sleep

class keypad(object):

	def __init__(self, RowPins, ColumnPins, Callback=None):
		self.RowPins = RowPins
		self.ColumnPins = ColumnPins
		self.Callback = Callback
		
		GPIO.setmode(GPIO.BCM)
		
		for pin in RowPins:
			GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.Pressed, bouncetime=250)
			
		for pin in ColumnPins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, 0)

	def Pressed(self, channel):
		# Get row
		for i, pin in enumerate(self.RowPins):
			if pin == channel:
				row = i
		
		# Get column
		column = -1
		for i, pin in enumerate(self.ColumnPins):
			if column < 0:
				GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				sleep(0.01)
				if GPIO.input(channel):
					column = i
			
		# Reset outputs
		for pin in self.ColumnPins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, 0)

		keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
		
		if (row >= 0) and (column >= 0):
			key = keys[row*3 + column]
			if self.Callback:
				self.Callback(key)
