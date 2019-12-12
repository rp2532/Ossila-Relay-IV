# Ossila-IV-measurement
Measure IV sweeps using an Ossila X200 source measure unit and Velleman VMA436 relay board controlled by an Arduino Uno

Instructions 
To run:
Open a command line (Windows: Start - Type CMD, hit enter. Mac: Open Terminal)
Navigate to the folder Ossila-Relay-IV (Type "cd" (without quotes), space, and copy-paste the path copied from the address bar in Computer hit enter) 
Type "python IVprogram_Windows.py" or "python IVprogram_Unix.py" (depending on what OS you are working in) and hit enter
The program GUI should open

To set up on a new computer:
Open IVprogram.py in a text editor (such as Notepad or Sublime Text)
Edit the Ossila IP address to the IP address that the Ossila SMU connected to this computer is assigned
Edit the Arduino COM port to the COM port that the Arduino connected to this computer is assigned
Save and close the file