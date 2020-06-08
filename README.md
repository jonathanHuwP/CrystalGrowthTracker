# Crystal Growth Tracker (CGT)

This project extracts data on the growth rates of individual faces from x-ray video shadowgraphs of growing crystals.

This algorithm and software was developed by Jonathan Pickering and Joanna Leng at the University of Leeds. They are both funded by EPSRC as part of Joanna Leng's Research Software Engineering Fellowship (EP/R025819/1).

Copyright 2020 Jonathan Pickering and Joanna Leng.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## DEVELOPED WITH: 
This was developed using Python 3.7 or above and Anaconda, Inc. on Windows 10 systems. The software has not been executed on Linux or Mac.

## QUICK START: 
Immediately below are a set of instructions that allow you to execute the CrytalGrowthTracker software quickly. There are no explanations of the steps here. Please look at the rest of the README file if you have any problems.

This software uses Anaconda with Python 3 so you will need to install and open an Anaconda shell. Once that is open, type the following the FIRST time you run the PERPL software (it is not required for later runs):

`conda env create -f environment_CGT.yml`

Next, activate the CGT Anaconda environment using the following command:

`conda activate CGT`

Compile the pyqt5 Code. 
 
`cd src`

`pyuic5 .\CrystalGrowthTrackerMain.ui -o .\Ui_CrystalGrowthTrackerMain.py`

Finally run the Crystal Growth Tracker:

`python .\CrystalGrowthTrackerMain.py`

In the future you will just need to start the CGT environment and then run the Crystal Growth Tracker.

## ENVIRONMENT:
The Anaconda environment, with all the necessary modules, can be set up using the *environment_CGT.yml* file. 

To see what conda environments you have, run the command

`conda env list`

To create a new Anaconda environment for CGT, run the command

`conda env create -f environment_CGT.yml`

To start using the environment, run the command

`conda activate CGT`

To stop using that enviroment:

`conda deactivate`

To remove the environment, if you no longer want to use CGT:

`conda remove --name CGT --all` 

## Notes for Developers

### QT5
The project uses the Python version of Qt for its GUI. This window is designed visually using a Qt Designer, and saved as a .ui file (XML descriptio of the window). The file is then compiled to an object stump that can be subcalssed.

To run the Qt Designer tool open a terminal (this could be an anaconda power shell) and run designer.exe:

`designer`

Button, slicers and other QWidgets communicate via message passing (signals to slots), which is set up using the Qt connect function. This can be specified in the ui by Designer, but (without extra custom scripting) Designer will not know the names of the functions you have written as slots. You can add them by right clicking on the design in Designer, select "Change signals/slots" then adding your slot. Alternativly you can connect the widget to the close function, save and close the design, and then hand edit the XML inserting the name of your function in place of close().

### IDEs (Integrated Development Environments)
Some IDE such as Spyder use QT5 for their GUI (Graphical User Interface). This can cause complications. The conda environment created for this application does not have Spyder included in it and if it were included it would not run. You will need to start Spyder from the Start menu or from a conda shell that does not use the environment for this application. 


You may like to use a IDE that does not use QT5 - some IDE that work well with Anaconda are given right at the very bottom of this web page:

https://docs.anaconda.com/anaconda/user-guide/getting-started/

#### Eclipse
Eclipe uses Java rather than QT5 for its windowing system and offers some advanced level of support for software devlopment. Details on its installation and setup are available here:
http://cis.bentley.edu/tbabaian/cs602/notes/setup-anaconda-eclipse-pydev.pdf

I had problems with this because I am running a Windows 10 system with a previously installed version of anaconda. For Eclipe to pick up the Anconda python interpreter correctly the Anaconda install needs to have the Anaconda Path added to the PATH environment variables. This is an Advanced option in the Anaconda install which is not normally recommended. To correct this I had to uninstall Anaconda and reinstall with this new option. I chose to do a full uninstall as given here:
https://stackoverflow.com/questions/48236584/python-how-can-i-completely-uninstall-anaconda-on-windows-10

This gives Eclipe the path for the base Anaconda environment but it best to work on the CGT environment. The environment install on a Windows system for the user called john is C:\Users\john\anaconda3\python.exe while for that use the CGT environment would be C:\Users\john\anaconda3\envs\CGT\python.exe. This needs to be added manually as an environment variable through the Control Panel. Editing the environment variables in Windows is considered an Advanced operation so be careful.

When you create the Eclipe project use the path code\CrystalGrowthTracker\src as the location for the project, this cannot be edited later.