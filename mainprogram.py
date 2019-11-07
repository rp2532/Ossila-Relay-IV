'''
OssilaMeasurement class attributes and methods
'''

import tkinter as tk
import numpy as np 
import os
import xtralien
from datetime import datetime

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

    def __init__(self, ipaddress):
        '''
        Initialize IVMeasurement object and create the GUI window
        '''
        # Accept and store ip address of Ossila unit passed during instance creation
        self.ipaddress = ipaddress

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

        # Device params
        self.devicename = 'testdevice'
        self.devicedescription = 'a great solar cell'

        # Create the GUI
        self.master = tk.Tk()
        self.master.title('IV sweep program') # Window title

        # Frames for input parameters and buttons
        self.setupframe = tk.Frame(self.master) # Frame for user-input setup parameters
        self.setupframe.grid(row=0, column=0)
        self.deviceframe = tk.Frame(self.master) # Frame for user-input device parameters
        self.deviceframe.grid(row=1, column=0)
        self.ivsweepframe = tk.Frame(self.master) # Frame for user-input IV sweep parameters
        self.ivsweepframe.grid(row=2, column=0)
        self.buttonframe = tk.Frame(self.master)
        self.buttonframe.grid(row=3, column=0)

        # Widgets for data entry
        # Setup params
        tk.Label(self.setupframe, text='Precision').grid(row=0,column=0)
        self.precision_entry = tk.Entry(self.setupframe)
        self.precision_entry.insert(0, self.precision)
        self.precision_entry.grid(row=0, column=1)

        tk.Label(self.setupframe, text='Range').grid(row=1,column=0)
        self.range_entry = tk.Entry(self.setupframe)
        self.range_entry.insert(0, self.range1)
        self.range_entry.grid(row=1, column=1)

        tk.Label(self.setupframe, text='Oversampling rate').grid(row=2,column=0)
        self.osr_entry = tk.Entry(self.setupframe)
        self.osr_entry.insert(0, self.osr1)
        self.osr_entry.grid(row=2, column=1)

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

        # Collect all user-input params in a function that is triggered by pressing Run button
        # Run button
        run_button = tk.Button(self.buttonframe, text='Run', command=self.run)
        run_button.grid(row=1, column=0)

        # Main loop
        self.master.mainloop()

    # Class methods
    def run(self):
        '''
        Main run IV sweep function
        '''
        # Collect and update all user-input params
        self.precision = int(self.precision_entry.get())
        self.range1 = int(self.range_entry.get())
        self.osr1 = int(self.osr_entry.get())
        self.devicename = self.devicename_entry.get()
        self.devicedescription = self.devicedescription_entry.get()
        self.vstart = float(self.vstart_entry.get())
        self.vstop = float(self.vstop_entry.get())
        self.vstep = float(self.vstep_entry.get())

        # Print user-input parameters 
        self.print_all_params()

        # Run IV sweep
        result = self.iv_sweep()

        # Plot result
        self.plot_result()

        # Save result to file
        self.save_result()

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
        with xtralien.X100.Network(self.ipaddress) as ossila:
            # Create voltage array
            voltages = np.arange(self.vstart, self.vstop, self.vstep)

            self.result = np.vstack([ossila.smu1.oneshot(v) for v in voltages])

    def plot_result(self):
        '''
        Plot IV result to Canvas on screen
        '''
        # Plot appearance settings
        sns.set(font_scale=2.)
        sns.set_style('ticks', {'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': True, 'grid.color': 'k', 'axes.edgecolor': 'k'})
        matplotlib.rcParams['lines.linewidth'] = 3.
        matplotlib.rcParams['axes.linewidth'] = 1.5
        matplotlib.rcParams['axes.titlesize'] = 12.
        header = 'Voltage (V),Current (A)'

        fig = Figure()
        fig1 = fig.add_subplot(111)
        fig1.plot(self.result[:,0], self.result[:,1])

        # Attach figure to canvas in master window
        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.get_tk_widget().grid(row=0, column=1)
        canvas.draw()

    def save_result(self):
        '''
        Save IV result to CSV file
        '''
        currenttime = str(datetime.now()) # to add timestamp to filename
        outfile = os.path.join(self.data_folder, self.devicename+' '+currenttime+'.csv')
        np.savetxt(outfile, result, delimiter=',', header=header)