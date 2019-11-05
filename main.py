'''
Main function for running Ossila code
'''

ipaddress = '192.168.1.199'
import ossilaX200 as ossila

# Setup
precision=3
range1=2
osr1=5
unsafe1=False
range2=2
osr2=5
unsafe2=False

# Initialize Ossila with given settings
ossila.initialize(ipaddress, precision=precision, range1=range1, osr1=osr1, unsafe1=unsafe1, range2=range2, osr2=osr2, unsafe2=unsafe2)

# Take measurement
#result = ossila.single_measurement(ipaddress, 0.0)

# Take IV sweep
result = ossila.iv_sweep(ipaddress, -0.1, 0.1, 0.01)

print(result)
