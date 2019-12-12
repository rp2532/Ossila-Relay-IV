ipaddress_ossila = '192.168.1.203'

# Clear previously generated pyc files
import os
os.system('rmdir -f ./__pycache__/*')

from mainprogram import *

iv = IVMeasurement(ipaddress_ossila, 'COM6')