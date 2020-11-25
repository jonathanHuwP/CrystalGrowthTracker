# Crystal Growth Tracker (CGT)

This project extracts data on the growth rates of individual faces from x-ray video shadowgraphs of growing crystals.

The algorithm and software in this project were developed by Jonathan Pickering and Joanna Leng at the University of Leeds. They are both funded by EPSRC as part of Joanna Leng's Research Software Engineering Fellowship (EP/R025819/1).

Copyright 2020 Jonathan Pickering and Joanna Leng.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## DEVELOPED WITH: 
This was developed using Python 3.7 or above and Anaconda, Inc. on Windows 10 systems. The software has not been executed on Linux or Mac.

## QUICK START: 
The followin instructions describe how you build and execute the CrytalGrowthTracker software. There are no explanations of the steps here. Please look at the rest of the README file if you have any problems.

### Install and First Run
This software uses Anaconda with Python 3 so you will need to install and open an Anaconda shell. Once that is open, type the following the FIRST time you run the software, it is not required for later runs. During the first two commands you may be asked to install additional conda packages, you have to allow conda to do this. If you have installed conda at a system level rather than in user space, you will need to have administrator privaleged. On windows right click on the 'Anaconda PowerShell Prompt' in the start menu and select "Run as Administrator".

`conda env create -f environment_CGT.yml`

To activate the CGT Anaconda environment type the following:

`conda activate CGT`

To build the Qt widgets reqired 

`python .\build_ui.py`

Finally run the Crystal Growth Tracker:

`python .\run_cgt.py`

### Runs Without Install
In the future you will just need to start the CGT environment and then run the Crystal Growth Tracker.

`conda activate CGT`
`python .\run_cgt.py`

## ENVIRONMENT:
The Anaconda environment, with all the necessary modules, can be set up using the *environment_CGT.yml* file. 

To see what conda environments you have, run the command

`conda env list`

To create a new Anaconda environment for CGT, run the command

`conda env create -f environment_CGT.yml`

To start using the environment, run the command

`conda activate CGT`

To stop using that environment:

`conda deactivate`

To remove the environment, if you no longer want to use CGT:

`conda remove --name CGT --all` 

## DOXYGEN DOCUMENTATION
Doxygen documentation for this project can be created. Python doxygen is part of the PERPL environment so you do not need to install doxygen.

Run the command in the top directory of the source code:

`doxygen`

After this has run a doc/html directory will appear. Open the index.html file in this directory.

The doxygen documentation for this project lists gives the API (Application Programmers Interface) for all the modules and scripts in this project making it useful to developers who wish to further develop this software.

## Notes for Developers

### QT5
The project uses the Python version of Qt for its GUI. This window is designed visually using a Qt Designer, and saved as a .ui file (XML description of the window). The file is then compiled to an object stump that can be subclassed.

To run the Qt Designer tool open a terminal (this could be an anaconda power shell) and run designer.exe:

`designer`

Button, slicers and other QWidgets communicate via message passing (signals to slots), which is set up using the Qt connect function. This can be specified in the ui by Designer, but (without extra custom scripting) Designer will not know the names of the functions you have written as slots. You can add them by right clicking on the design in Designer, select "Change signals/slots" then adding your slot. Alternatively, you can connect the widget to the close function, save and close the design, and then hand edit the XML inserting the name of your function in place of close().

### QT Translation

The code has been designed to allow translations of the user interface. The process of producing a translation is to extract the text strings needing translation from the .py and .ui files using the Qt program pylupdate5; then use Qt Linguist to read the strings file and add the translations; and finally save the translations as a binary .qm file. It is important to save the latest translation as a phrase book .qph file.  Linguist can open a phrase book alongside a translation file to allow quick filling of unchanged text, this avoids retranslating the entire interface because of the correction of a single typo.  The following describes the production of a translation for German, using an Anaconda PowerShell.

1. Use pylupdate5 to make a .ts file

    '''
    pylupdate5 .\CrystalGrowthTrackerMain.py .\CrystalGrowthTrackerMain.ui .\PolyLineExtract.py .\DrawRect.py .\ImageLabel.py -ts cgt_german.ts
    '''
2. Run 'linguist.exe', open the 'cgt_german.ts', if there is an existing phrase book load that as well.  Carry out the translation, and save the .ts file and save it again as a phrase book, overwriting the existing if necessary.

3. Save the .ts file a third time by selecting 'Release' or 'Release As' on Linguist's 'File' menu. 

4. Add the appropriate code to the *get_translators* function. Note if you want the buttons of Qt dialogs to be labelled you will have to load the appropriate *qtbase* file.

### IDEs (Integrated Development Environments)
Some IDE such as Spyder use QT5 for their GUI (Graphical User Interface). This can cause complications. The conda environment created for this application does not have Spyder included in it and if it were included it would not run. You will need to start Spyder from the Start menu or from a conda shell that does not use the environment for this application. 


You may like to use an IDE that does not use QT5 - some IDE that work well with Anaconda are given right at the very bottom of this web page:

https://docs.anaconda.com/anaconda/user-guide/getting-started/


#### Eclipse
Eclipe uses Java rather than QT5 for its windowing system and offers some advanced level of support for software devlopment. Details on its installation and setup are available here:
http://cis.bentley.edu/tbabaian/cs602/notes/setup-anaconda-eclipse-pydev.pdf

I had problems with this because I am running a Windows 10 system with a previously installed version of anaconda. For Eclipe to pick up the Anconda python interpreter correctly the Anaconda install needs to have the Anaconda Path added to the PATH environment variables. This is an Advanced option in the Anaconda install which is not normally recommended. To correct this I had to uninstall Anaconda and reinstall with this new option. I chose to do a full uninstall as given here:
https://stackoverflow.com/questions/48236584/python-how-can-i-completely-uninstall-anaconda-on-windows-10

This gives Eclipe the path for the base Anaconda environment but it best to work on the CGT environment. The environment install on a Windows system for the user called john is C:\Users\john\anaconda3\python.exe while for that use the CGT environment would be C:\Users\john\anaconda3\envs\CGT\python.exe. This needs to be added manually as an environment variable through the Control Panel. Editing the environment variables in Windows is considered an Advanced operation so be careful.

When you create the Eclipe project use the path code\CrystalGrowthTracker\src as the location for the project, this cannot be edited later.

To use pylint on your project through eclipe from the top menu select Window -> Prferences to open the preferences window. From the left hand list now select PyDev -> Builders and in this frame check that the "Use Builders?" options is selected. Now from the left hand list select PyDev -> Editor -> Code Analysis -> PyLint and in this frame select the severicty of the pylint outputs that you want to be displayed.

The pylint results are displayed in the problems window so you need to open this. It appears in the same frame and the Console and you need to click on its tab to see the contents of it. You can also edit what and how this displays results by select options through a drop down menu that is access by clicking on the 3 vertical dots at the top left of the problem frame. Errors and warnings are displyed in the problems window but information on conventions and refactoring are visible in the editor window.

As unnescessary white space is an output of pylint information you may also want to view the what spaces. Select Window -> Preferences and from the proferences window select General -> Editors -> Text Editors and here you can select a number of text display options including showing white space and configuring which caharature of those to include. 

