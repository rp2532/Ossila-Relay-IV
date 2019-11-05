'''
Ossila X200 SMU control code
'''
from xtralien import *
import numpy as np

def initialize(ipaddress, precision=3, range1=2, osr1=5, unsafe1=False, range2=2, osr2=5, unsafe2=False):
    with X100.Network(ipaddress) as dev:
        dev.cloi.set.precision(precision, response=False) # Set Precision for both SMUs
        dev.smu1.set.range(range1, response=False) # Set SMU1 range
        dev.smu1.set.osr(osr1, response=False) # Set SMU1 OSR
        dev.smu1.set.unsafe(unsafe1, response=False) # Set SMU1 unsafe
        dev.smu2.set.range(range2, response=False) # Set SMU2 range
        dev.smu2.set.osr(osr2, response=False) # Set SMU2 OSR
        dev.smu2.set.unsafe(unsafe2, response=False) # Set SMU2 unsafe

def single_measurement(ipaddress, voltage=0.0):
    with X100.Network(ipaddress) as dev:
		# Turn on SMU1
        print(dev.smu1.set.enabled(1, response=0))

		# Set voltage, measure voltage and current
        result = dev.smu1.oneshot(voltage)

    return result

def iv_sweep(ipaddress, vstart, vstop, vstep):
    with X100.Network(ipaddress) as dev:
        # Create voltage array
        voltages = np.arange(vstart, vstop, vstep)
        
        #debug
        print(voltages)
        result = np.vstack([dev.smu1.oneshot(v) for v in voltages])

    return result