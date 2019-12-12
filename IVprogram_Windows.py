ipaddress_ossila = '192.168.1.203'
arduino_com_port = 'COM6'

# Clear previously generated pyc files
import os
os.system('del /Q .\__pycache__\*')

from mainprogram import *

iv = IVMeasurement(ipaddress_ossila, arduino_com_port)