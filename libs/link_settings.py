##############################################################
# This is a straight up copy of the INMOS link-driver.h 
# file from the Linux kernel module.
#
# We kept it the same as we need to use several of the 
# staticly defined variables.
##############################################################

LINK_MAJOR = 24		# Major device number 
LINK_NAME = "link"		# Name of the device to register 
LINK_NO	= 2		# Number of supported boards 

# These are the link_table[].flags flags...
LINK_EXIST = 0x0001		# Is a B004-Board with at least one Transputer present ? 
LINK_BUSY = 0x0002		# Is the B004-board in use ? 
LINK_READ_ABORT = 0x0004 		# abort reading after timeout ? 
LINK_WRITE_ABORT = 0x0008 		# abort writing after timeout ? 

# IOCTL numbers
LINKTIME = 0x0001		# no longer available 
LINKRESET = 0x0012		# reset transputer 
LINKWRITEABLE = 0x0004		# check if we can send a byte 
LINKREADABLE = 0x0008		# check if we can receive a byte 
LINKANALYSE	= 0x0010		# go to analyse mode 
LINKERROR = 0x0020
LINKREADTIMEOUT	= 0x0040		# set timeout for reading 
LINKWRITETIMEOUT = 0x0080		# set timeout for writing 
LINKREADABORT = 0x0100
LINKWRITEABORT = 0x0200

# timeout for printk'ing a timeout, in jiffies (100ths of a second).
# This is also used for re-checking error conditions if LINK_READ_ABORT or 
# LINK_WRITE_ABORT is not set. This is the default behavior for reading.
# Writing has the timeout enabled per default.
 
LINK_INIT_WRITE_TIMEOUT	= 1000
LINK_INIT_READ_TIMEOUT = 100

#
# If the link interface is not ready for reading or writing the driver starts
# to poll the interface.
# At the begining, the driver sleeps for LINK_START_SLEEP jiffies. If the
# link interface is still unable to send or receive a byte, the driver
# sleeps again for the same duration.
# After LINK_INC times sleeping LINK_START_SLEEP jiffies, the driver adds one
# jiffy to its sleeping time. After LINK_INC times sleeping the new amount
# of time, it is incremented again and so on.
# The maximum time to sleep without rechecking the link interface is specified
# by LINK_MAX_SLEEP.
 

LINK_MAX_SLEEP = 20
LINK_START_SLEEP = 1
LINK_INC = 16

# The addresses of the C012 hardware registers relative to the
# base address.
LINK_IDR_OFFSET	= 0		# Input Data Register 
LINK_ODR_OFFSET	= 1		# Output Data Register 
LINK_ISR_OFFSET	= 2		# Input Status Register 
LINK_OSR_OFFSET	= 3		# Output Status Register 
LINK_RESET_OFFSET = 16		# Reset/Error Register 
LINK_ERROR_OFFSET = 16
LINK_ANALYSE_OFFSET	= 17		# Analyse Register 
B008_DMA_OFFSET	= 18		# B008: DMA request register 
B008_INT_OFFSET	= 19		# B008: Interrupt control reg 
B004_IO_SIZE = 20		# Some 'non' B008 boards have additional registers, allocate the space anyway! 
B008_IO_SIZE = 20

# Id's for the supported boards 
LINK_B004 = 1
LINK_B008 = 2

# bit defines for C012 reset/error port at base + 16 
LINK_ASSERT_RESET = 0x01	# resetting the transputer 
LINK_DEASSERT_RESET	= 0x00
LINK_TEST_ERROR	= 0x01	# for testing the transputer's error flag 

# bit defines for C012 analyse port at base + 17 
LINK_ASSERT_ANALYSE	= 0x01	# switch transputer to analyse-mode 
LINK_DEASSERT_ANALYSE = 0x00

# Some special sequences as taken from the original ispy check.c source code
SSRESETHI = [ 0, 0, 0, 0, 0, 1, 0, 0, 0 ]
SSRESETLO = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ] 
SSANALYSEHI = [ 0, 1, 0, 0, 0, 1, 0, 0, 0 ]
SSANALYSELO = [ 0, 1, 0, 0, 0, 0, 0, 0, 0 ]
BOOTSTRING = [ 23, 0xB1, 0xD1, 0x24, 0xF2, 0x21, 
				0xFC, 0x24, 0xF2, 0x21, 0xF8, 0xF0, 
				0x60, 0x5C, 0x2A, 0x2A, 0x2A, 0x4A, 
				0xFF, 0x21, 0x2F, 0xFF, 0x02, 0x00 ]
				
# Status codes as lifted from INMOS linkio.h
NULL_LINK = -1
SUCCEEDED = 0
ER_LINK_BAD	= -1
ER_LINK_CANT = -2
ER_LINK_SOFT = -3
ER_LINK_NODATA = -4
ER_LINK_NOSYNC = -5
ER_LINK_BUSY = -6
ER_NO_LINK = -7
ER_LINK_SYNTAX = -8