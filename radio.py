from time import sleep
from encoder import *
from rtlsdr import *
from RPLCD import CharLCD, BacklightMode, CursorMode
from keypad import *
import os

class radio:

	def __init__(self):
		# Settings.  Get from config file
		# self.Frequency = 434.250
		self.Modes = [
						{'label':  'USB', 'frequency': 434.250, 'largestep': 0.1, 'smallstep': 0.0005},
						{'label':  'LSB', 'frequency': 434.250, 'largestep': 0.1, 'smallstep': 0.0005},
						{'label':   'AM', 'frequency':  20.0,   'largestep': 1.0, 'smallstep': 0.1},
						{'label':   'FM', 'frequency': 434.250, 'largestep': 0.1, 'smallstep': 0.025},
						{'label':  'WFM', 'frequency':  90.2,   'largestep': 0.1, 'smallstep': 0.0005},
						{'label': 'APRS', 'frequency': 434.250, 'largestep':   0, 'smallstep': 0}
					 ]
		self.APRSModes = [
							{'label': 'US',	'frequency': 144.390},
							{'label': 'NZ',	'frequency': 144.575},
							{'label': 'JP',	'frequency': 144.660},
							{'label': 'EU',	'frequency': 144.800},
							{'label': 'AR',	'frequency': 144.930},
							{'label': 'AU',	'frequency': 145.175},
							{'label': 'BR',	'frequency': 145.570}
						 ]
		# self.Frequency = 90.8
		self.SmallStep = 0.1
		self.LargeStep = 1
		self.Mode = 0
		self.APRSMode = 0
		self.LargeSteps = False
		self.Volume = 80
		self.DataEntry = ''
		self.ModePressed = False

		# LCD
		self.lcd = CharLCD(pin_rs=21, pin_e=20, pins_data=[26, 19, 13, 6],
					  numbering_mode=GPIO.BCM,
					  cols=16, rows=2, dotsize=8,
					  auto_linebreaks=True,
					  pin_backlight=None, backlight_enabled=True,
					  backlight_mode=BacklightMode.active_low)
					  # pin_rw=... (not using this pin)
		
		for j in range(6):
			bar = []
			mask = 0
			for i in range(j):
				mask = mask | (1 << (4-i))
			for i in range(8):
				value = ((1 << (i-2)) - 1 if i>2 else 0) & mask
				bar = bar + [value]
			self.lcd.create_char(j, bar)

		# Dials
		self.f_dial = rotary_encoder(12, 16, 5, self.f_up, self.f_down, self.f_press)
		self.v_dial = rotary_encoder(8, 7, 1, self.v_up, self.v_down, self.v_press)
		
		# Keypad
		pad = keypad([0,11,9,10], [22,27,17], self.key_press)

		# SDR
		self.sdr = rtl_sdr()

		# Set default mode, frequency, volume etc
		self.set_frequency(self.Modes[self.Mode]['frequency'])
		self.set_volume(self.Volume)
		self.set_data_entry('')
		self.set_mode(0)
		
	def show_frequency(self):
		self.lcd.cursor_pos = (0, 0)
		self.lcd.write_string(" " * 11)
		self.lcd.cursor_pos = (0, 0)
		self.lcd.write_string("%8.4fMHz" % self.Modes[self.Mode]['frequency'])
		
	def set_frequency(self, new_frequency):
		self.Modes[self.Mode]['frequency'] = new_frequency
		self.sdr.set_frequency(self.Modes[self.Mode]['frequency'])
		self.show_frequency()
		
	def set_frequency_for_mode(self):
		if self.Modes[self.Mode]['label'] == 'APRS':
			frequency = self.APRSModes[self.APRSMode]['frequency']
		else:
			frequency = self.Modes[self.Mode]['frequency']
		self.set_frequency(frequency)
		
	def set_volume(self, new_volume):
		self.Volume = min(max(0, new_volume), 100)
		os.system("amixer cset numid=1 -- " + str(self.Volume) + "% > /dev/null")
		# self.lcd.cursor_pos = (1, 0)
		# self.lcd.write_string("Vol " + str(self.Volume) + " ")
		
	def show_mode(self):
		ModeString = self.Modes[self.Mode]['label'].rjust(4)
		self.lcd.cursor_pos = (0, 12)
		self.lcd.write_string(ModeString)
		
	def set_mode(self, mode):
		if mode < 0:
			self.Mode = len(self.Modes)-1
		elif mode >= len(self.Modes):
			self.Mode = 0
		else:
			self.Mode = mode
		self.show_mode()
		self.set_frequency_for_mode()
		
	def set_data_entry(self, line):
		self.DataEntry = line
		self.lcd.cursor_pos = (1, 0)
		self.lcd.write_string(" " * 16)
		if line == '':
			self.lcd.cursor_mode = CursorMode.hide
		else:
			self.lcd.cursor_pos = (1, 0)
			self.lcd.cursor_mode = CursorMode.blink
			self.lcd.write_string(line)

	def cancel_data_entry(self):
		self.set_data_entry('')
			
	def cancel_setting(self):
		self.set_data_entry('')
		self.lcd.cursor_pos = (1, 0)
		self.lcd.write_string(" " * 16)
			
	def key_press(self, key):
		if key == '*':
			self.cancel_data_entry()
		elif key == '#':
			self.set_frequency(float(self.DataEntry))
			self.set_data_entry('')
		else:
			if len(self.DataEntry) == 2:
				self.set_data_entry(self.DataEntry + key + '.')
			else:
				self.set_data_entry(self.DataEntry + key)


	def f_down(self):
		self.set_frequency(self.Modes[self.Mode]['frequency'] - (self.LargeStep if self.LargeSteps else self.SmallStep))

	def f_up(self):
		self.set_frequency(self.Modes[self.Mode]['frequency'] + (self.LargeStep if self.LargeSteps else self.SmallStep))
		
	def f_press(self):
		self.LargeSteps = not self.LargeSteps
		
	def v_down(self):
		if self.ModePressed:
			self.set_mode(self.Mode - 1)
		else:
			self.set_volume(self.Volume-5)

	def v_up(self):
		if self.ModePressed:
			self.set_mode(self.Mode + 1)
		else:
			self.set_volume(self.Volume+5)

	def v_press(self):
		self.ModePressed = not self.ModePressed
		self.cancel_data_entry()
		if self.ModePressed:
			self.lcd.cursor_pos = (1, 0)
			self.lcd.write_string("*Selecting Mode*")
		else:
			self.cancel_setting()
			self.show_frequency()

myradio = radio()
		
while 1:
	sleep(1)

GPIO.cleanup()           # clean up GPIO on normal exit 

# lcd.cursor_pos = (0, 0)
# lcd.write_string("Program Ended")
# lcd.close(clear=False)

