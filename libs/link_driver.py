#!/usr/bin/env python
##################################################
#
# An abstracted class to operate on an INMOS B004
# compatible Transputer interface.
#
# Requires the Linux kernel driver to be installed.
# Preferably the Linux 3.x.x driver as available
# at: http://github.com/megatron-uk/INMOS-Link-Driver
#
# By John Snowdon (john.snowdon@newcastle.ac.uk) 2016
#
##################################################

import sys
import os
import time
import fcntl
import traceback
from link_settings import LINKRESET

class Link():

	device = False
	config = False
	buf = []

	def __init__(self, link_config):
		self.config = link_config
		#for k in self.config.keys():
		#	print("%s : %s" % (k, self.config[k]))

	def OpenLink(self):
		try:
			self.device = os.open(self.config["link_device"], os.O_RDWR)
			return True
		except Exception as e:
			print("Error opening Transputer link device %s:" % self.config["link_device"])
			traceback.print_exc(file=sys.stdout)
			return False
	
	def CloseLink(self):
		try:
			if self.device:
				os.close(self.device)
			return True
		except Exception as e:
			print("Error closing Transputer link device %s:" % self.config["link_device"])
			traceback.print_exc(file=sys.stdout)
			return False
		
	def ReadLink(self, count):
		self.buf = []
		try:
			if self.device:
				tmp = os.read(self.device, count)
				for b in tmp:
					self.buf.append(ord(b))
				return len(self.buf)
			else:
				print("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			print("Error reading %s bytes from Transputer link device %s:" % (count, self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def WriteLink(self, bytes, count):
		try:
			if self.device:
				if count > len(bytes):
					bytes_written = os.write(self.device, bytearray(bytes[0:-1]))
				else:
					bytes_written = os.write(self.device, bytearray(bytes[0:count]))
				return bytes_written
			else:
				print("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			print("Error writing %s bytes to Transputer link device %s:" % (count, self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def ResetLink(self):
		try:
			if self.device:
				fcntl.ioctl(self.device, LINKRESET)
				return True
			else:
				print("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			print("Error sending reset to Transputer link device %s:" % (self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def AnalyseLink(self):
		pass
	
	def TestError(self):
		pass
	
	def TestRead(self):
		pass
	
	def TestWrite(self):
		pass
	
	def Wait(self, sleep = 0.01):
		time.sleep(sleep)
		return True
