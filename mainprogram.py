'''
OssilaMeasurement class attributes and methods
'''

import tkinter as tk
import numpy as np 
import os
import xtralien
from datetime import datetime
import time

# Packages for plotting and plot integration into Tkinter GUI
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns

class IVMeasurement:
    '''
    Commands to initialize and run measurements on Ossila X200
    '''

    def __init__(self, smu_ipaddress, verbose=False):
        '''
        Initialize IVMeasurement object and create the GUI window
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

        # Create the GUI
        self.master = tk.Tk()
        self.master.title('IV sweep program') # Window title

        # Frames for input parameters and buttons
        self.setupframe = tk.Frame(self.master) # Frame for user-input setup parameters
        self.setupframe.grid(row=0, column=0)
        self.range_selector_frame = tk.Frame(self.setupframe)
        self.range_selector_frame.grid(row=1,column=0)

        self.deviceframe = tk.Frame(self.master) # Frame for user-input device parameters
        self.deviceframe.grid(row=1, column=0)
        self.ivsweepframe = tk.Frame(self.master) # Frame for user-input IV sweep parameters
        self.ivsweepframe.grid(row=2, column=0)
        self.buttonframe = tk.Frame(self.master)
        self.buttonframe.grid(row=3, column=0)

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
        tk.Label(self.deviceframe, text='Device Name').grid(row=0,column=0)
        self.devicename_entry = tk.Entry(self.deviceframe)
        self.devicename_entry.insert(0, self.devicename)
        self.devicename_entry.grid(row=0, column=1)

        tk.Label(self.deviceframe, text='Device Description').grid(row=1,column=0)
        self.devicedescription_entry = tk.Entry(self.deviceframe)
        self.devicedescription_entry.insert(0, self.devicedescription)
        self.devicedescription_entry.grid(row=1, column=1)

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
        tk.Checkbutton(self.ivsweepframe, text='Forward sweep', var=self.checkbutton_forwardiv).grid(row=3, column=0)

        self.checkbutton_reverseiv = tk.BooleanVar()
        self.checkbutton_reverseiv.set(True)
        tk.Checkbutton(self.ivsweepframe, text='Reverse sweep', var=self.checkbutton_reverseiv).grid(row=4, column=0)

        self.checkbutton_lightiv = tk.BooleanVar()
        self.checkbutton_lightiv.set(True)
        tk.Checkbutton(self.ivsweepframe, text='Light IV', var=self.checkbutton_lightiv).grid(row=5, column=0)

        self.checkbutton_darkiv = tk.BooleanVar()
        self.checkbutton_darkiv.set(True)
        tk.Checkbutton(self.ivsweepframe, text='Dark IV', var=self.checkbutton_darkiv).grid(row=6, column=0)

        # Collect all user-input params in a function that is triggered by pressing Run button
        # Run button
        run_button = tk.Button(self.buttonframe, text='Run', command=self.run)
        run_button.grid(row=1, column=0)

        # Main loop
        self.master.mainloop()

    def __del__(self):
        '''
        Desctructor - exit appropriately by closing all open Ossila X100 Device instances
        '''
        for device in self.open_devices:
            device.close()

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
        self.pixels = ['A'] # TODO - replace with actual selector for pixels in GUI

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
                time.sleep(1)

                for self.sweep_direction in self.sweep_directions:
                    self.iv_sweep()

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
        self.vstart = float(self.vstart_entry.get())
        self.vstop = float(self.vstop_entry.get())
        self.vstep = float(self.vstep_entry.get())

        self.lightIV = self.checkbutton_lightiv.get()
        self.darkIV = self.checkbutton_darkiv.get()
        self.forwardIV = self.checkbutton_forwardiv.get()
        self.reverseIV = self.checkbutton_reverseiv.get()
        # TODO - collect pixel selections, once pixel switching is implemented

    def initialize_ossila(self):
        '''
        Connect to Ossila SMU over ethernet and set the self.ossila object
        '''
        self.ossila = xtralien.X100.Network(self.smu_ipaddress)
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

        # Plot the latest result
        self.plot_new_result()

    def initialize_plot(self):
        '''
        Create a plot in canvas on GUI window
        Set plot appearance settings
        '''
        # Plot appearance settings
        sns.set(font_scale=2.)
        sns.set_style('ticks', {'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': True, 'grid.color': 'k', 'axes.edgecolor': 'k'})
        matplotlib.rcParams['lines.linewidth'] = 1.5
        matplotlib.rcParams['axes.linewidth'] = 1.5
        matplotlib.rcParams['axes.titlesize'] = 12.

        # Create figure
        self.plot = Figure()
        self.subplot1 = self.plot.add_subplot(111)

        # Ticks and ticklabels
        ax = self.plot.gca()
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2e'))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))

        # Attach figure to canvas in master window
        self.plot_canvas = FigureCanvasTkAgg(self.plot, master=self.master)
        self.plot_canvas.get_tk_widget().grid(row=0, column=1)

    def plot_new_result(self):
        '''
        Plot the latest result to existing plot
        '''
        self.subplot1.plot(self.result[:,0], self.result[:,1])
        self.plot_canvas.draw()
        # TODO - update legend?

    def save_result(self):
        '''
        Save IV result to CSV file
        '''
        header = 'Voltage (V), Current (A)'
        currenttime = str(datetime.now()) # to add timestamp to filename
        outfile = os.path.join(self.data_folder, self.devicename+' '+currenttime+'.csv')

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