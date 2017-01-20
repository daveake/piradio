from RPi import GPIO

class rotary_encoder(object):

	def __init__(self, A, B, Button, CallbackUp=None, CallbackDown=None, CallbackPress=None):
		self.A = A
		self.B = B
		self.Button = Button
		self.CallbackUp = CallbackUp
		self.CallbackDown = CallbackDown
		self.CallbackPress = CallbackPress
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		GPIO.add_event_detect(A, GPIO.BOTH, callback=self.Edge, bouncetime=1)
		GPIO.add_event_detect(B, GPIO.BOTH, callback=self.Edge, bouncetime=1)
		GPIO.add_event_detect(Button, GPIO.FALLING, callback=self.Pressed, bouncetime=250)

	def Pressed(self, channel):
		if self.CallbackPress:
			self.CallbackPress()
			
	def Edge(self, channel):
		if channel == self.A:
			if GPIO.input(self.A):
				if not GPIO.input(self.B):
					if self.CallbackDown:
						self.CallbackDown()
		else:
			if GPIO.input(self.A):
				if not GPIO.input(self.B):
					if self.CallbackUp:
						self.CallbackUp()

