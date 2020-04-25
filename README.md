# CrystalGrowthTracker

Extract data on the growth rates of individual faces from x-ray video shadowgraphs of growing crystals.

## Compiling pyqt5 Code

The project uses the Python version of Qt for its GUI. In this window is designed visually using a Qt Designer, and saved as a .ui file (XML descriptio of the window). The file is then compiled to an object stump that can be subcalssed.
 
1. You will need to install the pyqt5 modules using pip or conda

2. In an Anaconda terminal (Powershell or Terminal) run:> pyuic5 .\CrystalGrowthTrackerMain.ui -o .\Ui_CrystalGrowthTrackerMain.py

3. To run Qt Designer open a terminal and run designer.exe

Button, slicers and other QWidgets communicate via message passing (signals to slots), which can is set up using the Qt connect function. This can be specified in the ui by Designer, but (without extra custom scripting) Designer will not know the names of the functions you have written as slots. You can add them by right clicking on the design in Designer, select "Change signals/slots" then adding your slot. Alternativly you can connect the widget to the close function, save and close the design, and then hand edit the XML inserting the name of your function in place of close(). 


