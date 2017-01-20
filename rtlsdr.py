import socket, sys

from RPi import GPIO

class rtl_sdr(object):

	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.connect(("localhost", 6020))
		
	def set_frequency(self, Frequency):
		buf = b'\x00'
		data = int(Frequency * 1000000.0)		# MHz to Hz

		for i in range(4):
			buf = buf + chr(data & 0xff)
			# buf = buf + bytes([data & 0xff])	# python 3 version
			data = data >> 8

		self.s.send(buf)

		
		# s.close()
