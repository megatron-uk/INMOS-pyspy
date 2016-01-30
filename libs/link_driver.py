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

# python modules
import sys
import os
import time
import fcntl
import traceback

# hardcoded values and return code types
from link_settings import LINKRESET
# a python logging tool
from link_logger import link_logger	
	
class Link():
	""" A class which interacts with the Linux device-driver for INMOS B004 
	compatible Transputer link hardware. Should be useable by any Python
	code wanting to interact with the Transputer network. """

	device = False
	config = False
	buf = []

	def __init__(self, link_config):
		self.config = link_config
		if self.config["device_verbose"]:
			self.logger = link_logger(__name__, 'DEBUG')
			self.logger.debug(self.config)
		else:
			self.logger = link_logger(__name__, 'WARN')

	def OpenLink(self):
		try:
			self.logger.debug("Opening %s" % (self.config["link_device"]))
			self.device = os.open(self.config["link_device"], os.O_RDWR)
			self.logger.debug("Opened!")
			return True
		except Exception as e:
			self.logger.fatal("Error opening Transputer link device %s:" % self.config["link_device"])
			traceback.print_exc(file=sys.stdout)
			return False
	
	def CloseLink(self):
		try:
			if self.device:
				self.logger.debug("Closing %s" % self.config["link_device"])
				os.close(self.device)
				self.logger.debug("Closed!")
			else:
				self.logger.warn("Transputer link device %s is not open" % self.config["link_device"])
			return True
		except Exception as e:
			self.logger.fatal("Error closing Transputer link device %s:" % self.config["link_device"])
			traceback.print_exc(file=sys.stdout)
			return False
		
	def ReadLink(self, count):
		self.buf = []
		try:
			if self.device:
				self.logger.debug("Reading %s bytes from %s" % (count, self.config["link_device"]))
				tmp = os.read(self.device, count)
				for b in tmp:
					self.buf.append(ord(b))
				return len(self.buf)
			else:
				self.logger.warn("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			print("Error reading %s bytes from Transputer link device %s:" % (count, self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def WriteLink(self, bytes, count):
		try:
			if self.device:
				self.logger.debug("Writing %s bytes to %s" % (count, self.config["link_device"]))
				if count > len(bytes):
					self.logger.debug(" ".join(hex(n) for n in bytes[0:-1]))
					bytes_written = os.write(self.device, bytearray(bytes[0:-1]))
				else:
					self.logger.debug(" ".join(hex(n) for n in bytes[0:count]))
					bytes_written = os.write(self.device, bytearray(bytes[0:count]))
				return bytes_written
			else:
				self.logger.warn("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			self.logger.fatal("Error writing %s bytes to Transputer link device %s:" % (count, self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def ResetLink(self):
		try:
			if self.device:
				self.logger.debug("Resetting Transputer link device %s" % (self.config["link_device"]))
				fcntl.ioctl(self.device, LINKRESET)
				return True
			else:
				self.logger.warn("Transputer link device %s is not open" % self.config["link_device"])
				return False
		except Exception as e:
			self.logger.fatal("Error sending reset to Transputer link device %s:" % (self.config["link_device"]))
			traceback.print_exc(file=sys.stdout)
			return False
	
	def AnalyseLink(self):
		self.logger.debug("Not implemented")
		return True
	
	def TestError(self):
		self.logger.debug("Not implemented")
		return True
	
	def TestRead(self):
		self.logger.debug("Not implemented")
		return True
	
	def TestWrite(self):
		self.logger.debug("Not implemented")
		return True
	
	def Wait(self, sleep = 0.01):
		self.logger.debug("Sleeping %s" % (sleep))
		time.sleep(sleep)
		return True
