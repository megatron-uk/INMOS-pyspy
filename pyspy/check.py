#!/usr/bin/env python
################################################################
#
# check.py - Roughly analogous to the old C check.c file from ispy.
#
# Loads a program onto the root Transputer of a network to
# determine the network map, transputer type, speed, etc.
#
# Needs a working Linux kernel driver - only tested on my modern
# Linux 3.x.x driver, as available from:
# https://github.com/megatron-uk/INMOS-Link-Driver
#
# Based on check.c from ispy by Andy Rabagliati INMOS and Jeremy Thorp.
#
# check.py by John Snowdon (John.Snowdon@newcastle.ac.uk) 2016.
#
###############################################################

import sys
import time
from libs.link_settings import SSRESETLO, SSRESETHI, BOOTSTRING, ER_LINK_NOSYNC
import libs.link_hardware as link_hardware

################################################################

def solve():
	pass

################################################################

def findtype(link):
	
	# Try to boot the root transputer by sending it
	# a very small program.
	bytes = link.WriteLink(BOOTSTRING, len(BOOTSTRING))
	if (bytes == len(BOOTSTRING)):
		
		link.Wait()
		going = True
		bytes = []
		cnt = 0	
		# Read back the data as returned by the code now
		# running on the root transputer cpu. This should
		# start with several bytes describing the transputer type.
		while (going):
			read_result = link.ReadLink(1)
			cnt += 1
			if (cnt >= 30):
				going = False
			
			if (read_result == 1):
				bytes = bytes + link.buf
			
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
				print("Failed to determine root Transputer type, received 2 bytes")
				sys.exit(2)
			
		if len(bytes) == 4:
			if ((bytes[0] == 0xAA) and (bytes[1] == 0xAA)):
				# Found a T32
				return link_hardware.T32
			else:
				print("Failed to determine root Transputer type, received 4 bytes")
				sys.exit(2)
		
		print("Failed to determine root Transputer type")
		sys.exit(2)
		
	else:
		print("Failed to boot root Transputer")
		sys.exit(2)

################################################################

def check(link):
	
	
	if link.config["root_reset"]:
		# Try and do a root transputer subsystem reset
		status = link.ResetLink()
		if (status == False):
			print("Unable to reset root transputer")
			sys.exit(2)
		
	if link.config["root_subsys_reset"]:
		# Try and reset subsystems
		bytes = link.WriteLink(SSRESETLO, len(SSRESETLO))
		if (bytes != len(SSRESETLO)):
			print("Failed to reset subsystem port 1")
			sys.exit(2)
		link.Wait()
		
		bytes = link.WriteLink(SSRESETHI, len(SSRESETHI))
		if (bytes != len(SSRESETHI)):
			print("Failed to reset subsystem port 2")
			sys.exit(2)
		link.Wait()
		
		bytes = link.WriteLink(SSRESETLO, len(SSRESETLO))
		if (bytes != len(SSRESETLO)):
			print("Failed to reset subsystem port 3")
			sys.exit(2)
		link.Wait()	
		
	# Find details of the root transputer
	findtype(link)
