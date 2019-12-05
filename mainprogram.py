'''
OssilaMeasurement class attributes and methods
'''

import tkinter as tk
import numpy as np 
import os
import xtralien # Ossila X200 package
from datetime import datetime
import time

# Packages for plotting and plot integration into Tkinter GUI
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns

# Packages for Phidget relay
from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *

class IVMeasurement:
    '''
    Commands to initialize and run measurements on Ossila X200
    '''

    def __init__(self, smu_ipaddress, verbose=False):
        '''
        Initialize IVMeasurement object, create the GUI window, attach Phidget relay
        '''
        # Accept and store ip address of Ossila unit passed during instance creation
        self.smu_ipaddress = smu_ipaddress
        self.verbose = verbose
        self.initialized = False

        # Maintain a list of all running Ossila X100 Device instances
        # Used for closing them (and their connections) appropriately upon exit
        self.open_devices = []

        # Create instance variables for all parameters and set default values
        # Setup params
        self.precision = 4
        self.range1 = 2
        self.osr1 = 5
        self.unsafe1 = False
        self.range2 = 2
        self.osr2 = 5
        self.unsafe2 = False
        self.data_folder = './'

        # IV sweep params
        self.vstart = -0.2 # V
        self.vstop = 0.2 # V
        self.vstep = 0.01 # V
        self.lightIV = True # Run light IV sweep?
        self.darkIV = True # Run dark IV sweep?
        self.forwardIV = True # Run forward IV sweep?
        self.reverseIV = True # Run reverse IV sweep?

        self.sweep_directions = []
        self.shutter_conditions = []
        self.pixels = []

        # Device params
        self.devicename = 'testdevice'
        self.devicedescription = 'v good solar cell'
        self.devicearea = 0.1033 # cm^2

        # Create Phidget channels
        self.phidgetchannel = DigitalOutput()
        self.phidgetchannel.setDeviceSerialNumber(563146)
        self.phidgetchannel.setHubPort(0)
        '''
        self.phidgetchannels = []
        for i in range(6):
            self.phidgetchannels.append(DigitalOutput())
            # Set serial number of hub port
            self.phidgetchannels[i].setDeviceSerialNumber(563146) 
            # Set hub port that the relay is connected to 
            self.phidgetchannels[i].setHubPort(0)
            # Set channel number
            self.phidgetchannels[i].setChannel(i)
            # Open channel
            #self.phidgetchannels[i].open()
            self.phidgetchannels[i].openWaitForAttachment(5000)
        '''

        # Create the GUI
        self.master = tk.Tk()
        self.master.title('IV sweep program') # Window title

        # Frames for input parameters and buttons
        self.setupframe = tk.Frame(self.master) # Frame for user-input setup parameters
        self.setupframe.grid(row=0, column=0, pady=10)
        self.range_selector_frame = tk.Frame(self.setupframe)
        self.range_selector_frame.grid(row=1,column=0, pady=10)

        self.deviceframe = tk.Frame(self.master) # Frame for user-input device parameters
        self.deviceframe.grid(row=1, column=0, pady=10)
        self.pixelselectorframe = tk.Frame(self.master)
        self.pixelselectorframe.grid(row=2, column=0, pady=10)
        self.ivsweepframe = tk.Frame(self.master) # Frame for user-input IV sweep parameters
        self.ivsweepframe.grid(row=3, column=0, pady=20)
        self.whichsweepsframe = tk.Frame(self.master) # Frame for selecting forward and reverse sweeps and light and dark
        self.whichsweepsframe.grid(row=4, column=0, pady=10)
        self.buttonframe = tk.Frame(self.master)
        self.buttonframe.grid(row=5, column=0, pady=10)

        # Widgets for data entry
        # Setup params
        tk.Label(self.setupframe, text='Precision (decimal places)').grid(row=0,column=0)
        self.precision_entry = tk.Entry(self.setupframe)
        self.precision_entry.insert(0, self.precision)
        self.precision_entry.grid(row=0, column=1)

        # Range selector
        tk.Label(self.range_selector_frame, text='Range').grid(row=1,column=0)
        self.range_tkvar = tk.IntVar()
        self.range_tkvar.set(2)
        tk.Radiobutton(self.range_selector_frame, text='150 mA', var=self.range_tkvar, value=1).grid(row=2, column=0)
        tk.Radiobutton(self.range_selector_frame, text='20 mA', var=self.range_tkvar, value=2).grid(row=2, column=1)
        tk.Radiobutton(self.range_selector_frame, text='2 mA', var=self.range_tkvar, value=3).grid(row=2, column=2)
        tk.Radiobutton(self.range_selector_frame, text='200 uA', var=self.range_tkvar, value=4).grid(row=2, column=3)
        tk.Radiobutton(self.range_selector_frame, text='20 uA', var=self.range_tkvar, value=5).grid(row=2, column=4)

        # Device params
        tk.Label(self.deviceframe, text='Device Name').grid(row=0, column=0)
        self.devicename_entry = tk.Entry(self.deviceframe)
        self.devicename_entry.insert(0, self.devicename)
        self.devicename_entry.grid(row=0, column=1)

        tk.Label(self.deviceframe, text='Device Description').grid(row=1, column=0)
        self.devicedescription_entry = tk.Entry(self.deviceframe)
        self.devicedescription_entry.insert(0, self.devicedescription)
        self.devicedescription_entry.grid(row=1, column=1)

        tk.Label(self.deviceframe, text='Device Area (cm2)').grid(row=2, column=0)
        self.devicearea_entry = tk.Entry(self.deviceframe)
        self.devicearea_entry.insert(0, self.devicearea)
        self.devicearea_entry.grid(row=2, column=1)

        # Pixel selector
        tk.Label(self.pixelselectorframe, text='Pixels').grid(row=0, column=0)

        # Variable to hold pixels selected
        self.pixel_selection = []
        self.pixel_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        self.num_devices_per_pixel = 6
        for i in range(self.num_devices_per_pixel):
            self.pixel_selection.append(tk.BooleanVar())
            tk.Checkbutton(self.pixelselectorframe, text=self.pixel_letters[i], variable=self.pixel_selection[i]).grid(row=1, column=i)
        self.pixel_selection[0].set(True) # Set pixel A alone to be enabled by default

        # IV sweep params 
        tk.Label(self.ivsweepframe, text='V start').grid(row=0,column=0)
        self.vstart_entry = tk.Entry(self.ivsweepframe)
        self.vstart_entry.insert(0, self.vstart)
        self.vstart_entry.grid(row=0, column=1)

        tk.Label(self.ivsweepframe, text='V stop').grid(row=1,column=0)
        self.vstop_entry = tk.Entry(self.ivsweepframe)
        self.vstop_entry.insert(0, self.vstop)
        self.vstop_entry.grid(row=1, column=1)

        tk.Label(self.ivsweepframe, text='V step').grid(row=2,column=0)
        self.vstep_entry = tk.Entry(self.ivsweepframe)
        self.vstep_entry.insert(0, self.vstep)
        self.vstep_entry.grid(row=2, column=1)

        self.checkbutton_forwardiv = tk.BooleanVar()
        self.checkbutton_forwardiv.set(False)
        tk.Checkbutton(self.whichsweepsframe, text='Forward sweep', var=self.checkbutton_forwardiv).grid(row=0, column=0)

        self.checkbutton_reverseiv = tk.BooleanVar()
        self.checkbutton_reverseiv.set(True)
        tk.Checkbutton(self.whichsweepsframe, text='Reverse sweep', var=self.checkbutton_reverseiv).grid(row=1, column=0)

        self.checkbutton_lightiv = tk.BooleanVar()
        self.checkbutton_lightiv.set(True)
        tk.Checkbutton(self.whichsweepsframe, text='Light IV', var=self.checkbutton_lightiv).grid(row=0, column=1)

        self.checkbutton_darkiv = tk.BooleanVar()
        self.checkbutton_darkiv.set(True)
        tk.Checkbutton(self.whichsweepsframe, text='Dark IV', var=self.checkbutton_darkiv).grid(row=1, column=1)

        # Collect all user-input params in a function that is triggered by pressing Run button
        # Run button
        run_button = tk.Button(self.buttonframe, text='Run', command=self.run)
        run_button.grid(row=1, column=0)

        # Main loop
        self.master.mainloop()

    def __del__(self):
        '''
        Desctructor - exit appropriately by closing all open Ossila Device instances
        '''
        # Close open Ossila devices
        for device in self.open_devices:
            device.close()
        # Close open Phidget channels
        #for i in range(6):
        #    self.phidgetchannels[i].close()
        self.phidgetchannel.close()

    # Class methods
    def run(self):
        '''
        Main run IV sweep function
        ''' 
        # Collect and update all user-input params
        self.collect_user_parameters()

        # Compile lists of sweeps to run
        if self.lightIV:
            self.shutter_conditions.append('open')
        if self.darkIV:
            self.shutter_conditions.append('closed')
        if self.reverseIV:
            self.sweep_directions.append('reverse')
        if self.forwardIV:
            self.sweep_directions.append('forward')

        for i in range(self.num_devices_per_pixel):
            if self.pixel_selection[i].get():
                self.pixels.append(i)

        # Print user-input parameters if desired
        if self.verbose:
            self.print_all_params()

        # Initialize Ossila SMU
        if not self.initialized:
            self.initialize_ossila()
            self.initialized = True

         # Create figure to plot in 
        self.initialize_plot()

        # Run all IV sweeps
        for self.pixel in self.pixels:
            for self.shutter_condition in self.shutter_conditions:
                # Set shutter appropriately and wait a second for it to execute
                self.set_shutter(self.shutter_condition)
                #debug
                #time.sleep(0.5)

                # Switch phidget relay to current pixel to be measured
                self.phidgetchannel.setChannel(self.pixel)
                self.phidgetchannel.openWaitForAttachment(2000)
                self.phidgetchannel.setState(True)

                for self.sweep_direction in self.sweep_directions:
                    self.iv_sweep()

                # Turn off phidget relay for current pixel
                self.phidgetchannel.setState(False)
                self.phidgetchannel.close()

                # Save result to file
                self.save_result()

        # Reinitialize list of scans to run to be empty lists
        self.reset_tasklist()

    def reset_tasklist(self):
        '''
        Create or reset to empty the tasklist of IV scans to be taken
        '''
        self.sweep_directions = []
        self.shutter_conditions = []
        self.pixels = []

    def collect_user_parameters(self):
        '''
        Collect and update all user-input params
        '''
        self.precision = int(self.precision_entry.get())
        self.range1 = int(self.range_tkvar.get())
        self.devicename = self.devicename_entry.get()
        self.devicedescription = self.devicedescription_entry.get()
        self.devicearea = float(self.devicearea_entry.get())
        self.vstart = float(self.vstart_entry.get())
        self.vstop = float(self.vstop_entry.get())
        self.vstep = float(self.vstep_entry.get())

        self.lightIV = self.checkbutton_lightiv.get()
        self.darkIV = self.checkbutton_darkiv.get()
        self.forwardIV = self.checkbutton_forwardiv.get()
        self.reverseIV = self.checkbutton_reverseiv.get()

    def initialize_ossila(self):
        '''
        Connect to Ossila SMU over ethernet and set the self.ossila object
        '''
        self.ossila = xtralien.X100.Network(self.smu_ipaddress)
        self.ossila.smu1.set.enabled(1, response=0)
        self.open_devices.append(self.ossila)

    def print_all_params(self):
        '''
        Print current values of all user-input parameters
        '''
        # Setup parameters
        print('Setup Parameters')
        print('Precision: ' + str(self.precision))
        print('Range 1: ' + str(self.precision))
        print('Oversampling Rate 1: ' + str(self.osr1))
        print('Range 2: ' + str(self.range2))
        print('Oversampling Rate 2: ' + str(self.osr2))

        # Device parameters
        print('Device Parameters')
        print('Device Name: ' + str(self.devicename))
        print('Device Description: ' + str(self.devicedescription))

        # IV sweep parameters
        print('IV Sweep Parameters')
        print('V start: ' + str(self.vstart))
        print('V stop: ' + str(self.vstop))
        print('V step: ' + str(self.vstep))

    def iv_sweep(self):
        '''
        Run IV sweep
        '''
        # Create voltage array
        voltages = np.arange(self.vstart, self.vstop, self.vstep)

        # Use appropriate sweep direction
        if self.sweep_direction == 'reverse':
            voltages = np.flipud(voltages)

        # Run IV sweep, store result in instance variable
        self.result = np.vstack([self.ossila.smu1.oneshot(v) for v in voltages])

        # Divide current by area to return current density
        # Multiply current by 1000 to return current in mA
        self.result[:,1] = self.result[:,1]*1000/self.devicearea

        # Plot the latest result
        self.plot_new_result()

    def initialize_plot(self):
        '''
        Create a plot in canvas on GUI window
        Set plot appearance settings
        '''
        # Plot appearance settings
        sns.set(font_scale=1.5)
        sns.set_style('ticks', {'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': True, 'grid.color': 'k', 'axes.edgecolor': 'k'})
        matplotlib.rcParams['lines.linewidth'] = 1.5
        matplotlib.rcParams['axes.linewidth'] = 1.5
        matplotlib.rcParams['axes.titlesize'] = 12.
        matplotlib.rcParams['xtick.labelsize'] = 12.
        matplotlib.rcParams['ytick.labelsize'] = 12.
        matplotlib.rcParams['legend.fontsize'] = 10.

        # Create figure
        self.plot = Figure()
        self.subplot1 = self.plot.add_subplot(111)

        # Ticks and ticklabels
        ax = self.plot.gca()
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2e'))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))

        # Axis labels
        ax.yaxis.set_label('J (mA cm-2)')
        ax.xaxis.set_label('V (V)')

        # Attach figure to canvas in master window
        self.plot_canvas = FigureCanvasTkAgg(self.plot, master=self.master)
        self.plot_canvas.get_tk_widget().grid(row=0, rowspan=5, column=1)
        self.plot_canvas.draw()

    def plot_new_result(self):
        '''
        Plot the latest result to existing plot
        '''
        self.label = 'px' + self.pixel_letters[int(self.pixel)]
        if self.shutter_condition == 'open':
            self.label = self.label + '_' + 'light'
        else:
            self.label = self.label + '_' + 'dark'
        if self.sweep_direction == 'forward':
            self.label = self.label + '_' + 'forward' 
        else:
            self.label = self.label + '_' + 'reverse'
        self.subplot1.plot(self.result[:,0], self.result[:,1], label=self.label)
        self.subplot1.legend(loc='upper left')
        self.plot_canvas.draw()

    def save_result(self):
        '''
        Save IV result to CSV file
        '''
        header = str(datetime.now()) # First line of header - current time
        header = header + '\nDevice Name,' + self.devicename
        header = header + '\nDevice Description,' + self.devicedescription
        header = header + '\nDevice Area,' + str(self.devicearea)
        header = header + '\nPixel,' + self.pixel_letters[self.pixel]

        header = header + '\nPrecision,' + str(self.precision)
        header = header + '\nRange,' + str(self.range1)
        header = header + '\nV start,' + str(self.vstart)
        header = header + '\nV stop,' + str(self.vstop)
        header = header + '\nV step,' + str(self.vstep)

        header = header + '\nSweep direction,' + self.sweep_direction

        if self.shutter_condition == 'open':
            header = header + '\nShutter,' + 'light'
        else:
            header = header + '\nShutter,' + 'dark'

        header = header + '\nVoltage (V),Current (A)'
        currenttime = str(datetime.now()) # to add timestamp to filename
        #outfile = os.path.join(self.data_folder, self.devicename+' '+currenttime+'.csv')
        
        outfile = self.devicename + str(self.pixel) + '.csv'
        np.savetxt(outfile, self.result, delimiter=',', header=header)
        

    def set_shutter(self, state='closed'):
        '''
        Open or close the shutter
        '''
        if state == 'closed':
            # Set shutter output to 0 V
            self.ossila.shutter.set(False)
        elif state == 'open':
            # Set voltage on SMU output
            self.ossila.shutter.set(True)