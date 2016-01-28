# INMOS-pyspy
Updated versions of the INMOS Transputer user tools ispy and mtest, implemented in Python using my new Linux kernel driver.

## Useage

The -pyspy.py- script takes almost all the same options as the old -ispy- tool; reset root processor, reset subsystem, set link device, information mode, etc.

Requires the Linux 3.x.x INMOS Link Driver kernel module to be loaded and an INMOS B004/B008 compatible Transputer interface to be installed in the system. Yes, this means all 5 of us in the world who still own one in the 21st Century...

## Limitations

The -pyspy.py- tool currently detects the root Transputer and can reset processor and subsystems. It does not yet map the Transputer network or print CPU details or link speeds.

No -mtest.py- tool yet. Sorry.
