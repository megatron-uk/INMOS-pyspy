#!/usr/bin/env python
################################################################
#
# check.py: Roughly analogous to the old C check.c file from ispy.
# check.py: by John Snowdon (John.Snowdon@newcastle.ac.uk) 2016.
#
# Loads a program onto the root Transputer of a network to
# determine the network map, transputer type, speed, etc.
#
# Needs a working Linux kernel driver - only tested on my modern
# Linux 3.x.x driver, as available from:
# https://github.com/megatron-uk/INMOS-Link-Driver
#
# Based on check.c and cklib.c from the old ispy source code
# as written by Andy Rabagliati INMOS and Jeremy Thorp.
#
###############################################################

# Basic Python modules
import sys
import time

# defines, fixed values, lookup tables etc
from libs.link_settings import SSRESETLO, SSRESETHI, BOOTSTRING, ER_LINK_NOSYNC
# A python logging tool to debug text
from libs.link_logger import link_logger
# more defines about particular hardware types
import libs.link_hardware as link_hardware


###############################################################

# Main programme code for the runtime check utility that executes on a Transputer
BOOTCODE = [
	0x8B,0x25,0x0A,0x21,0xF5, 0x71,0x60,0xEE,0x72,0x71, 0x60,0xEF,0x60,0x43,0x21, 
	0xFB,0x71,0x60,0xED,0x71, 0x70,0x73,0xF7,0x71,0x60, 0x5D,0x23,0xFC,0x34,0xF6,
	0x11,0x70,0x44,0x23,0xF4, 0xF7,0x71,0x83,0x62,0x47, 0x21,0xFB,0x84,0xFA,0xD1,
	0x61,0x4D,0x21,0xFB,0x71, 0x60,0x5D,0xF9,0xA6,0x61, 0x44,0x21,0xFB,0x53,0xD1,
	0x71,0x73,0xF2,0x41,0x23, 0xF4,0x60,0x8F,0xF5,0x41, 0x23,0xF4,0x23,0xF2,0x81,
	0x24,0xF6,0xD2,0x74,0x71, 0xF2,0xD4,0x70,0x41,0x23, 0xF4,0x22,0xFC,0x43,0x24,
	0xF6,0x65,0x08,0xD0,0xD0, 0x66,0x4E,0x21,0xFB,0x60, 0x5B,0x23,0xFC,0xD0,0xD0,
	0x24,0xF2,0xD1,0x71,0x21, 0xFC,0x71,0x21,0xF8,0x22, 0xF9,0x25,0xF7,0x40,0x25,
	0xF4,0x40,0xD2,0x4B,0xD3, 0x71,0x72,0x71,0xFA,0xE0, 0x12,0x49,0x22,0xF1,0x66,
	0x06,0,0,0,0 ]

TPBOOT = [ 0xFF, 0xFF, link_hardware.TAG_BOOT ]

# A data structure which holds boot code for INMOS 32bit transputers.
TYPE32 = {
	'code' 			: [
	0x20,0x20,0x60,0xB2, 0x21,0x20,0x47,0x21, 0xFB,0xD4,0x24,0xF2, 
	0xDA,0x24,0xF2,0x51, 0xDB,0x24,0xF2,0x52, 0xDC,0x24,0xF2,0x53, 
	0xDD,0x24,0xF2,0x54, 0xD6,0x24,0xF2,0x55, 0xD7,0x24,0xF2,0x56, 
	0xD8,0x24,0xF2,0x57, 0xD9,0x7F,0x1A,0xFA, 0xD5,0x42,0xD1,0x2D, 
	0x4A,0x21,0xFB,0xD0, 0x4A,0x21,0xFB,0x60, 0xD7,0x60,0x18,0x23, 
	0xF9,0x60,0xB5,0x1B, 0xF3,0x21,0x77,0x1E, 0xFA,0xD6,0x1A,0xD1, 
	0x60,0x49,0x61,0x4D, 0x40,0x21,0x27,0xFC, 0xD5,0xD4,0x74,0xC0, 
	0xAE,0x75,0x28,0x20, 0x20,0x40,0x25,0xF6, 0xD0,0x10,0x71,0x42, 
	0x24,0xFA,0x0D,0x74, 0x28,0x20,0x20,0x40, 0x25,0xF6,0xD0,0x10, 
	0x71,0x42,0x24,0xFA, 0x71,0x10,0x42,0x24, 0xFA,0x70,0x2F,0x2F, 
	0x2F,0x4F,0x24,0xF6, 0x28,0x20,0x20,0x40, 0x23,0xFA,0x60,0xC9, 
	0x22,0xA0,0x7C,0x32, 0xD0,0x10,0x28,0xFE, 0x10,0x28,0xFE,0x28, 
	0xFF,0xC0,0xA4,0x29, 0xF0,0x60,0xAC,0x10, 0x28,0xF8,0x7C,0x32, 
	0x70,0xF4,0xC0,0xA6, 0x7C,0x51,0x71,0x42, 0x24,0xFA,0x22,0xF2, 
	0xD3,0x23,0x2E,0x48, 0x24,0xF1,0x22,0xF2, 0xD2,0x23,0x2F,0x4C, 
	0x72,0x73,0xF4,0x22, 0xFC,0x21,0x20,0x40, 0x21,0xF3,0x1A,0x82, 
	0x23,0xFB,0x21,0x77, 0x21,0x20,0x40,0x21, 0xF3,0x1A,0x83,0x23, 
	0xFB,0x1A,0x51,0xD7, 0x40,0xD0,0x10,0x76, 0x30,0x41,0xF7,0x22, 
	0xF2,0xD3,0x24,0xF2, 0x21,0x2C,0x50,0x76, 0x30,0x21,0x20,0x40, 
	0xF7,0x22,0xF2,0xD2, 0x72,0x73,0xF4,0x28, 0x20,0x20,0x40,0x25, 
	0xF6,0xD0,0x10,0x77, 0x42,0x24,0xFA,0x7D, 0x30,0xD0,0x7C,0x70, 
	0x42,0xFB,0x1A,0x70, 0x46,0xFB,0x21,0x2F, 0xFF,0x10,0x81,0x23, 
	0xF9,0x21,0xF5,0x18, 0xF3,0xBE,0x22,0xF0, 0x06,0x00,0x00,0x00, 
	0xF8,0xFF,0xFF,0xFF, 0x00,0x00,0x80,0x7F ],
	'target' 		: "TA",
	'mode' 			: "Undefined",
	'codesize'		: 284,
	'offset'		: 2,
	'workspace'		: 27,
	'vectorspace'	: 0,
	'bytesperword'	: 4,
	'totalspace'	: 392
}

# A data structure which holds boot code for INMOS 16bit transputers. 
TYPE16 = {
	'code' 			: [
	0x60,0xB1,0x24,0xF2, 0xD8,0x24,0xF2,0x51, 0xD9,0x24,0xF2,0x52, 
	0xDA,0x24,0xF2,0x53, 0xDB,0x24,0xF2,0x54, 0xD4,0x24,0xF2,0x55, 
	0xD5,0x24,0xF2,0x56, 0xD6,0x24,0xF2,0x57, 0xD7,0x21,0x70,0x18, 
	0xFA,0xD3,0x21,0x70, 0x14,0xFA,0xD2,0x42, 0xD1,0x28,0x46,0x21, 
	0xFB,0xD0,0x4B,0x21, 0xFB,0x68,0xD8,0x68, 0x19,0x23,0xF9,0x68, 
	0xB6,0x28,0x1A,0xF3, 0x29,0x13,0xD5,0x60, 0x49,0x61,0x4D,0x40, 
	0x21,0x27,0xFC,0xD6, 0xD4,0x74,0xC0,0xA4, 0x76,0x75,0xE0,0x03, 
	0x74,0x75,0xE0,0x22, 0xF2,0xD3,0x23,0x2E, 0x48,0x24,0xF1,0x22, 
	0xF2,0xD2,0x23,0x2F, 0x4C,0x72,0x73,0xF4, 0x22,0xFC,0x21,0x20, 
	0x40,0x21,0xF3,0x29, 0x13,0x51,0x23,0xFB, 0x29,0x77,0x21,0x20, 
	0x40,0x21,0xF3,0x29, 0x13,0x83,0x23,0xFB, 0x29,0x13,0x52,0xD1, 
	0x40,0xD0,0x10,0x28, 0x79,0x30,0x41,0xF7, 0x22,0xF2,0xD3,0x17, 
	0x28,0x79,0x30,0x21, 0x20,0x40,0xF7,0x22, 0xF2,0xD2,0x72,0x73, 
	0xF4,0x71,0xE0,0x28, 0x7A,0x30,0xD1,0x71, 0x46,0xFF,0x29,0x13, 
	0x71,0x46,0xFB,0x21, 0x2F,0xFF,0x10,0x81, 0x23,0xF9,0x21,0xF5, 
	0x28,0x17,0xF3,0xBF, 0x22,0xF0 ],
	'target' 		: "TA",
	'mode' 			: "Undefined",
	'codesize'		: 186,
	'offset'		: 0,
	'workspace'		: 155,
	'vectorspace'	: 0,
	'bytesperword'	: 2,
	'totalspace'	: 496
}

SEGSIZE = 511

###############################################################

class PData():
	""" A data class which holds data about a single transputer 
	processor and its links. """
	
	def __init__(self):
		self.tpid = 0
		self.bootlink = 255
		self.linkspeed = 0.0
		self.links = {
			'0' : False,
			'1' : False,
			'2' : False,
			'3' : False,
		}
		self.linkno = {
			'0' : None,
			'1' : None,
			'2' : None,
			'3' : None,
		}
		self.routelen = 0
		self.parent = False
		self.next = False
		self.info = []
		self.tptype = False
		
	def __str__(self):
		return("tpid:%s tptype: %s bootlink:%s linkspeed:%s routelen:%s" % (self.tpid, self.tptype, self.bootlink, self.linkspeed, self.routelen))

###############################################################

class Check():
	""" This is the main network-worm check class. It is initialised with an
	instance of a link_driver object. """
	
	
	def __init__(self, link = None):
		self.link = link
		self.logger = link_logger(__name__, 'WARN')
		if self.link.config["verbose"]:
			self.logger = link_logger(__name__, 'INFO')
		if self.link.config["vverbose"]:
			self.logger = link_logger(__name__, 'DEBUG')
			self.logger.debug(self.link.config)			
		self.readbytes_buf = []
		self.readbytes_length = 0
		

	################################################################
	
	def readbytes(self, maxlength = 0):
		""" """
		
		bytes_to_go = maxlength
		bytes_read = []
		count = 10
		bytes_read_count = 0
			
		self.logger.debug("readbytes maxlength: %s" % maxlength)
			
		while ((bytes_to_go > 0) and (count > 0)):
		 	bytes_read_count = self.link.ReadLink(count = bytes_to_go)
		 	bytes_read = bytes_read + self.link.buf
			self.logger.debug("loop - readbytes(bytesread = %s)" % bytes_read_count)
			bytes_to_go -= bytes_read_count
			count -= 1
	
		if (bytes_read_count < 0):
			self.logger.warn("Read from link failed - result = %s" % bytes_read_count)
			bytes_read_count = 0;
		else:
			if (count == 0):
				self.logger.warn("Read from link failed (Timeout)")
			else:
				bytes_read_count = maxlength - bytes_to_go
	
		self.logger.debug("readbytes(bytesread = %s)" % bytes_read_count)
	
		self.readbytes_buf = bytes_read
		return bytes_read_count
		
	################################################################

	def getiserver(self, maxlength = 0):
		""" """
		self.readbytes_buf = []
		self.readbytes_length = 0
		self.logger.debug("Querying iserver")
		if (self.readbytes(maxlength = 2) == 2):
			self.readbytes_length = (self.readbytes_buf[1] << 8) + self.readbytes_buf[0]
			if ((self.readbytes_length <= maxlength) and (self.readbytes_length) and (self.readbytes(maxlength = self.readbytes_length) == self.readbytes_length)):
				return True
			else:
				if (self.readbytes_length):
					return False
				else:
					# length of zero
					return True
		else:
			return False

	################################################################
	
	def getstats(self, processor = None):
		""" """
		
		self.logger.debug("Getstats running for processor %s" % processor.tpid)
		if ((self.getiserver(maxlength = 6)) and (self.readbytes_length == 6)):
			tptype = self.readbytes_buf[0] + (self.readbytes_buf[1] << 8)
			if (processor.tptype == link_hardware.T32):
				processor.tptype = tptype;
			elif ((processor.tptype == link_hardware.T16) and (tptype == link_hardware.T_414)):
				processor.tptype = link_hardware.T_212;
			
			processor.bootlink = self.readbytes_buf[3]
			processor.links[processor.bootlink] = processor.parent
			
			if (processor.parent):
				processor.linkno[processor.bootlink] = processor.route
				processor.parent.linkno[processor.route] = processor.bootlink
			else:
				processor.linkno[processor.bootlink] = link_hardware.HOST_TAG
			
			processor.procspeed = self.readbytes_buf[2]
			processor.linkspeed = float(self.readbytes_buf[4] + (self.readbytes_buf[5] << 8))
			if (processor.linkspeed != 0.0):
				processor.linkspeed = float(256.0E6 / processor.linkspeed)
			return processor
		else:
			self.logger.fatal("%s Partial results : Error reading Transputer %s type information" % ( i, processor.tpid))

	################################################################
	
	def linkspeed(self, processor = None):
		""" Determine how fast a specific transputer link is. """
		
		linkspeed = [ 0xFF, 0xFF, TAG_LSPEED ]
		self.logger.debug("Testing link speed to processor %s" % processor.tpid)
		self.setroute(processor = processor.parent, lastlink = processor.route)
		if (self.link.WriteLink(bytes = linkspeed, count = 3) == 3):
			return
		else:
			self.logger.fatal("Timed out testing link speed for processor %s" % processor.tpid)
			self.link.CloseLink()
			sys.exit(2)

	################################################################

	def setroute(self, processor = None, lastlink = None):
		""" Record which are the available links on a given processor. """
		
		self.logger.debug("Running setroute  for processor %s" % processor.tpid)
		new_processor = PData()
		route = [None] * (processor.routelen + 1)
		route[processor.routelen] = lastlink
	
		#for (i = p->routelen, q = p; 
		#	(i > 0) && (q != NULL); 
		#	i--, q = q->parent) {
		#	route[i - 1] = (unsigned char) q->route;
		#}
		i = processor.routelen
		while (i > 0):
			new_processor = processor
			route[i - 1] = new_processor.route
			i = i - 1
			self.logger.debug("i: %s route: %s new_processor: %s" % (i, route, new_processor))
		
		return processor
	
	################################################################
	
	def tpboot(self, processor = None):
		""" Prepares a transputer processor for booting. """
		
		if processor.parent:
			self.logger.debug("Sending pre-boot to processor %s" % processor.tpid)
			processor = self.setroute(processor = processor.parent, lastlink = processor.route)
			bytes = link.WriteLink(bytes = TPBOOT, count = len(TPBOOT))
			if bytes == 3:
				self.logger.info("Sent pre-boot code over link to processor %s" % processor.tpid)
				return processor
			else:
				self.logger.fatal("Error sending pre-boot code to processor %s" % processor.tpid)
				link.CloseLink()
				sys.exit(2)
		else:
			return processor
	
	################################################################
	
	def sendiserver(self, codesize = 0, bytes = []):
		""" iserver is a very small kernel which is uploaded to a
		transputer processor which we can then use to run commands for
		use - for example detecting amount of ram, link speed etc. """
		
		buf = []
		buf[0] = codesize & 0xFF
		buf[1] = codesize >> 8
		
		self.logger.debug("Sending iserver code to processor")
		if (self.link.WriteLink(buf, 2) == 2):
			
			written = self.link.WriteLink(bytes = bytes, count = codesize)
			if (written == codesize):
				return True
			else:
				self.logger.fatal("Unable to send iserver code to processor")
				return False
		else:
			return False
	
	################################################################
	
	def load(self, processor = None, codesize = 0, offset = 0, workspace = 0, vectorspace = 0, bytesperword = 0, code = []):
		""" Uploads basic runtime data onto a transputer which can 
		detect the type and model of processor, the amount of ram and
		other details. Needs iserver running on the processor first. """
		
		params = []
		processor = self.tpboot(processor = processor)
		
		length = codesize
		
		# Load first phase of iserver transputer code
		if processor.parent:
			self.logger.info("iserver 1 on %s" % processor.tpid)
			flag = self.sendiserver(codesize = len(BOOTCODE), bytes = BOOTCODE) 
		else:
			self.logger.info("writelink 1 on %s" % processor.tpid)
			if (self.link.WriteLink(bytes = BOOTCODE, count = len(BOOTCODE))) == len(BOOTCODE):
				flag = True
			else:
				flag = False
			
		self.link.Wait()
		if flag:
			j = 0
			for i in range(0, bytesperword, 1):
				params.append(workspace & 0xFF)
				workspace = workspace >> 8
				j += 1
				
			for i in range(0, bytesperword, 1):
				params.append(vectorspace & 0xFF)
				vectorspace = vectorspace >> 8
				
			for i in range(0, bytesperword, 1):
				params.append(codesize & 0xFF)
				codesize = codesize >> 8
				
			for i in range(0, bytesperword, 1):
				params.append(offset & 0xFF)
				offset = offset >> 8
			
			# Load second phase of iserver code
			if processor.parent:
				self.logger.info("iserver 2 on %s" % processor.tpid)
				flag = self.sendiserver(count = (4 * bytesperword), bytes = params);
			else:
				self.logger.info("writelink 2 on %s" % processor.tpid)
				if (self.link.WriteLink(bytes = params, count = (4 * bytesperword)) == (4 * bytesperword)):
					flag = True
				else:
					flag = False
					
			# Load third phase of iserver code
			i = 0
			count = 0
			while (i < length):	
				count = length - i;
				if (count > SEGSIZE):
					count = SEGSIZE				
				if processor.parent:
					self.logger.info("iserver 3 on %s" % processor.tpid)
					flag = self.sendiserver(count = count, bytes = code[i:count]);
				else:
					self.logger.info("writelink 3 on %s" % processor.tpid)
					if (self.link.WriteLink(bytes = code[i:count], count = count) == count):
						flag = True
					else:
						flag = False
				i += count
				if flag is False:
					break
				
			self.logger.info("load finished %s" % flag)
			return processor
		else:
			self.logger.fatal("Unable to load bootcode on transputer %s" % processor.tpid)
			self.link.CloseLink()
			sys.exit(2)
	
	################################################################
	
	def solve(self):
		pass
	
	################################################################
	
	def findtype(self):
		""" Determines the class of a transputer by sending it a small
		section of code which it runs and then sends back over one of its 
		links several status bytes. """
		
		# Try to boot the root transputer by sending it
		# a very small program.
		bytes = self.link.WriteLink(BOOTSTRING, len(BOOTSTRING))
		if (bytes == len(BOOTSTRING)):
			
			self.link.Wait()
			going = True
			bytes = []
			cnt = 0	
			# Read back the data as returned by the code now
			# running on the root transputer cpu. This should
			# start with several bytes describing the transputer type.
			while (going):
				read_result = self.link.ReadLink(1)
				cnt += 1
				if (cnt >= 30):
					going = False
				
				if (read_result == 1):
					bytes = bytes + self.link.buf
				
				if (read_result == ER_LINK_NOSYNC):
					going = False
				
				if (len(bytes) == 4):
					going = False
		
			if len(bytes) == 1:
				# Found a C4
				return link_hardware.C4
				
			if len(bytes) == 2:
				if ((bytes[0] == 0xAA) and (bytes[1] == 0xAA)):
					# Found a T16
					return link_hardware.T16
				else:
					self.logger.fatal("Failed to determine root Transputer type, received 2 bytes")
					self.link.CloseLink()
					sys.exit(2)
				
			if len(bytes) == 4:
				if ((bytes[0] == 0xAA) and (bytes[1] == 0xAA)):
					# Found a T32
					return link_hardware.T32
				else:
					self.logger.fatal("Failed to determine root Transputer type, received 4 bytes")
					self.link.CloseLink()
					sys.exit(2)
			
			self.logger.fatal("Failed to determine root Transputer type")
			self.link.CloseLink()
			sys.exit(2)
			
		else:
			self.logger.fatal("Failed to boot root Transputer")
			self.link.CloseLink()
			sys.exit(2)
	
	################################################################
	
	def check(self):
		""" Check the basic transputer network is present, resetting
		root processor and subsystems if needed, and then boot each
		transputer in turn, detecting the type and capabilities of 
		each one. """
		
		if self.link.config["root_reset"]:
			# Try and do a root transputer subsystem reset
			status = self.link.ResetLink()
			if (status == False):
				self.logger.fatal("Unable to reset root transputer")
				self.link.CloseLink()
				sys.exit(2)
			else:
				self.logger.info("Reset root transputer")
			
		if self.link.config["root_subsys_reset"]:
			# Try and reset subsystems
			bytes = self.link.WriteLink(SSRESETLO, len(SSRESETLO))
			if (bytes != len(SSRESETLO)):
				self.logger.fatal("Failed to reset subsystem port 1")
				self.link.CloseLink()
				sys.exit(2)
			else:
				self.logger.info("Reset subsystem 1")
			self.link.Wait()
			
			bytes = self.link.WriteLink(SSRESETHI, len(SSRESETHI))
			if (bytes != len(SSRESETHI)):
				self.logger.fatal("Failed to reset subsystem port 2")
				self.link.CloseLink()
				sys.exit(2)
			else:
				self.logger.info("Reset subsystem 2")
			self.link.Wait()
			
			bytes = self.link.WriteLink(SSRESETLO, len(SSRESETLO))
			if (bytes != len(SSRESETLO)):
				self.logger.fatal("Failed to reset subsystem port 3")
				self.link.CloseLink()
				sys.exit(2)
			else:
				self.logger.info("Reset subsystem 3")
			self.link.Wait()	
			
		# Find details of the root transputer
		p = PData()
		p.tptype = self.findtype()
		self.logger.info("Detected root transputer class")
	
		going = True
		
		# Keep running this loop until we've found all
		# the transputers which are connected to the root
		# processor by all of its links, and then all of
		# their links.
		while (going):
			
			self.logger.info("Attempting to load code on to Transputer %s" % p.tpid)
			# Try and load 16bit boot code on the transputer
			if (p.tptype == link_hardware.T16):
				success = self.load(processor = p, 
						codesize = TYPE16['codesize'],
						offset = TYPE16['offset'],
						workspace = TYPE16['workspace'],
						vectorspace = TYPE16['vectorspace'],
						bytesperword = TYPE16['bytesperword'],
						code = TYPE16['code'])
				if success is False:
					self.logger.fatal("Failed to load TYPE16 code on Transputer %s" % p.tpid)
					self.link.CloseLink()
					sys.exit(2)
				else:
					p = success
					self.logger.info("Loaded TYPE16 class transputer")
				
			# Try to load 32bit boot code on the transputer
			if (p.tptype == link_hardware.T32):
				success = self.load(processor = p, 
						codesize = TYPE32['codesize'],
						offset = TYPE32['offset'],
						workspace = TYPE32['workspace'],
						vectorspace = TYPE32['vectorspace'],
						bytesperword = TYPE32['bytesperword'],
						code = TYPE32['code'])
				if success is False:
					self.logger.fatal("Failed to load TYPE32 code on Transputer %s" % p.tpid)
					self.link.CloseLink()
					sys.exit(2)
				else:
					p = success
					self.logger.info("Loaded TYPE32 class transputer")
			
			# Test the link interface speed to this transputer
			self.logger.info("Testing speed to Transputer %s" % p.tpid)
			print p
			if p.routelen == 0:
				self.logger.debug("Using root processor test")
				tmpbuffer = [0x00] * 257
				written = self.link.WriteLink(bytes = tmpbuffer, count = 257)
				if written != 257:
					self.logger.fatal("Failed sending all data during link speed test")
					self.link.CloseLink()
					sys.exit(2)
			else:
				self.logger.debug("Using linkspeed processor test")
				self.linkspeed(p)
			self.logger.debug("Speed test completed")
				
			# Get stats
			p = self.getstats(processor = p)
			print p
			time.sleep(10)