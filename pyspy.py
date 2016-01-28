#!/usr/bin/env python

import sys
import getopt
from libs.link_driver import Link
from pyspy.check import check

PROGRAM_NAME="pyspy"
VERSION_NUMBER=0.1
DEFAULT_LINK="/dev/link0"

CONFIG = {
	'root_reset' : False,
	'root_subsys_reset' : False,
	'C004_read' : False,
	'C004_long_read' : False,
	'C004_reset' : False,
	'link_device' : DEFAULT_LINK,
	'verbose' : False
}

def help():
	print("\nUsage:  %s [--option...]\n" % (PROGRAM_NAME))
	print("		A Python based utility to test the connectivity of a")
	print("		Transputer network using the Linux kernel device driver.\n")
	print("		pyspy was written by John Snowdon (http://github.com/megatron-uk)")
	print("		Inspired by ispy (C) Andy Rabagliati")
	print("")
	print("Options:")
	print(" --n       :  do not reset the root transputer")
	print(" --r       :  reset the root transputer subsystem")
	print(" --c4      :  read the state of all C004s found")
	print(" --cl      :  read the state of C004s, long form")
	print(" --cr      :  reset all C004s found")
	print(" --l=<dev> :  use this link device, else %s" % DEFAULT_LINK)
	print(" --v       :  verbose mode")
	print(" --i       :  information - synonym for verbose mode")
	print(" --h       :  This help page\n")
	print("v%s" % VERSION_NUMBER)


def __main__():
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "nrlivh", ["i", "v", "r", "n", "c4", "cl", "cr", "cs", "l="])
	except getopt.GetoptError:
		help()
		sys.exit(2)
		
	output = None
	verbose = False
	for o, a in opts:
		if o == "--v":
			CONFIG["verbose"] = True
		elif o == "--i":
			CONFIG["verbose"] = True
		elif o == "--l":
			CONFIG["link_device"] = a
		elif o == "--n":
			CONFIG["root_reset"] = True
		elif o == "--r":
			CONFIG["root_subsys_reset"] = True
		elif o == "--c4":
			CONFIG["C004_read"] = True
		elif o == "--cl":
			CONFIG["C004_long_read"] = True
		elif o == "--cr":
			CONFIG["C004_reset"] = True
		elif o in ("--h", "--help"):
			help()
			sys.exit()
	
	# Create a new Link driver
	l = Link(CONFIG)
	print("%s v%s" % (PROGRAM_NAME, VERSION_NUMBER))	
	print("Attempting to open %s" % CONFIG["link_device"])
	if l.OpenLink():
		check(l)
	else:
		print("Unable to continue")
		sys.exit(2)
		
	print("Attempting to close %s" % CONFIG["link_device"])
	l.CloseLink()
	exit(0);
	
if __name__ == "__main__":
    __main__()
