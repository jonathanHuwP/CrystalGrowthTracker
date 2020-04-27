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

Finally, compile the pyqt5 Code. 
 
`cd src`

`pyuic5 .\CrystalGrowthTrackerMain.ui -o .\Ui_CrystalGrowthTrackerMain.py`

Run the QT environment.

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

## QT5:

The project uses the Python version of Qt for its GUI. This window is designed visually using a Qt Designer, and saved as a .ui file (XML descriptio of the window). The file is then compiled to an object stump that can be subcalssed.

3. To run Qt Designer open a terminal and run designer.exe

Button, slicers and other QWidgets communicate via message passing (signals to slots), which can is set up using the Qt connect function. This can be specified in the ui by Designer, but (without extra custom scripting) Designer will not know the names of the functions you have written as slots. You can add them by right clicking on the design in Designer, select "Change signals/slots" then adding your slot. Alternativly you can connect the widget to the close function, save and close the design, and then hand edit the XML inserting the name of your function in place of close(). 