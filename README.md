# Crystal Growth Tracker (CGT)

This project extracts data on the growth rates of individual faces from x-ray video shadowgraphs of growing crystals.

The algorithm and software in this project were developed by Jonathan Pickering and Joanna Leng at the University of Leeds. They are both funded by EPSRC as part of Joanna Leng's Research Software Engineering Fellowship (EP/R025819/1).

Copyright 2020 Jonathan Pickering and Joanna Leng.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Developed With:
This was developed using Python 3.8/3.9/3.10 and Anaconda, on Windows 10 systems, and also successfully tested on Ubuntu 20. The software has not been tested under any other operating systems.

## Installation, Use and Development
This software uses Anaconda with a Python version greater than 3.8. The packages required to run the software are listed in the file environment_CGT.yml.

If you have installed Anaconda, you can install the software and run in two steps:

### Quick Start: Set-up the Environment and Build the Software

Download through the gitHub web interface or clone from gitHub, to clone:

`git clone https://github.com/jonathanHuwP/CrystalGrowthTracker.git`

Open an Anaconda shell and navigate to the CrystalGrowthTracker directory.

Set up the conda environment:

`conda env create -f environment_CGT.yml`

To activate the CGT Anaconda environment type the following:

`conda activate cgt`

To build the Qt widgets reqired

`python .\build_ui.py`

### Changing or updating the environment

If you need to change or replace an old environment following the inculsion or removal of a package.

List conda environments:

`conda env list`

Update all packages in the current conda environment:

`conda update --all` or

Update cgt from a new .yml file:

`conda env update --name cgt --file environment.yml`

If you need to remove old environments:

`conda env remove --name cgt`

The enviroment can be recreated as described above.

### Running the Software

Open an Anaconda shell and activate the environment:

`conda activate cgt`

then navigate to the CrystalGrowthTracker directory and run by typing:

`python .\run_cgt.py`

you can also run from another directory using:

`python C:\Users\uname\Work\CrystalGrowthTracker\run_cgt.py`

or the path relative to your current location.

### Install with Pip

The software can be installed using pip, if you are in Anaconda the installation will be in the current enviroment.  To install open a command tool navigate to the project home directory and run the following commands.

`python build_ui.py`
`python setup.py build`
`python setup.py sdist`
`python setup.py clean`
`pip install -e .`

The project will now be installed with the name cgt, which has the same command line fundtions as run_cgt.py. The options can be listed by running

`cgt --help`

### Remove the Software

To remove software delete the CrystalGrowthTracker direcory, then delete the environment:

`conda remove --name cgt --all`

## Notes for Developers

The following are intended for developers wishing to extend CrystalGrowthTracker.

For information on how to contribute the project, please refer to the
[CONTRIBUTING](contributing.md) file at the top level of the repositary.

### Doxygen Documentation

The software is documented with doxygen.

`conda activate cgt`

Then, in the CrystalGrowthTracker direcory, run the command:

`doxygen`

After this has run a doc/html directory will appear. Open the index.html file in this directory.

The doxygen documentation for this project lists gives the API (Application Programmers Interface) for all the modules and scripts in this project making it useful to developers who wish to further develop this software.

### UnitTesting

Unit tests are in the directory 'cgt\tests', which also contains a module for building a dummy restults object.  All he tests can be run using the python script 'cgt\tests\run_tests.py'.  Any individual test module can be run by running the file itself `python tests\test_io.py` for example.

The script `run_unittests_2_csv.py` will run all the unit test printing results to a comma seperated value (.csv) file.

The tests are written using the Python unittest module and can also be run using the unittest command line, see [unittest man pages] (https://docs.python.org/3/library/unittest.html).  QWidgets are tested using the [PyQt5.QTest](https://doc.qt.io/qtforpython-5/PySide2/QtTest/QTest.html) module to generate simulated user events.

### Other Tests

Tests of the subprocess calls to ffmpeg cannot be carried out in unittest so the seperate program videosource_ffmpeg_test.py is provided. Please run this in the cgt enviroment.

### Combined Testing

Both unit tests and ffmpeg tests can be run by running the command

`python run_cgt.py -t`

or, if the project has been pip installed,

`cgt -t`

### QT5

The project uses the Python version of Qt for its GUI. This window is designed visually using a Qt Designer, and saved as a .ui file (XML description of the window). The file is then compiled to an object stump that can be subclassed.

To run the Qt Designer tool open a terminal (this could be an anaconda power shell) and run designer.exe:

`designer`

Button, slicers and other QWidgets communicate via message passing (signals to slots), which is set up using the Qt connect function. This can be specified in the ui by Designer, but (without extra custom scripting) Designer will not know the names of the functions you have written as slots. You can add them by right clicking on the design in Designer, select "Change signals/slots" then adding your slot. Alternatively, you can connect the widget to the close function, save and close the design, and then hand edit the XML inserting the name of your function in place of close().

### QT Translation

The code has been designed to allow translations of the user interface. The process of producing a translation is to extract the text strings needing translation from the .py and .ui files using the Qt program pylupdate5; then use Qt Linguist to read the strings file and add the translations; and finally save the translations as a binary .qm file. It is important to save the latest translation as a phrase book .qph file.  Linguist can open a phrase book alongside a translation file to allow quick filling of unchanged text, this avoids retranslating the entire interface because of the correction of a single typo.  The following describes the production of a translation for German, using an Anaconda PowerShell.

1. Use pylupdate5 to make a .ts file

    `pylupdate5 .\\CrystalGrowthTrackerMain.py .\\CrystalGrowthTrackerMain.ui .\\PolyLineExtract.py .\\DrawRect.py .\\ImageLabel.py -ts cgt_german.ts`

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

This gives Eclipe the path for the base Anaconda environment but it best to work on the CGT environment. The environment install on a Windows system for the user called uname is C:\\Users\\uname\\anaconda3\\python.exe while for that use the CGT environment would be C:\\Users\\uname\\anaconda3\\envs\\CGT\\python.exe. This needs to be added manually as an environment variable through the Control Panel. Editing the environment variables in Windows is considered an Advanced operation so be careful.

When you create the Eclipe project use the path code\\CrystalGrowthTracker\\src as the location for the project, this cannot be edited later.

To use pylint on your project through eclipe from the top menu select *Window -> Prferences* to open the preferences window. From the left hand list now select *PyDev -> Builders* and in this frame check that the "Use Builders?" options is selected. Now from the left hand list select *PyDev -> Editor -> Code Analysis -> PyLint* and in this frame select the severicty of the pylint outputs that you want to be displayed.

The pylint results are displayed in the problems window so you need to open this. It appears in the same frame and the Console and you need to click on its tab to see the contents of it. You can also edit what and how this displays results by select options through a drop down menu that is access by clicking on the 3 vertical dots at the top left of the problem frame. Errors and warnings are displyed in the problems window but information on conventions and refactoring are visible in the editor window.

As unnescessary white space is an output of pylint information you may also want to view the what spaces. Select *Window -> Preferences* and from the proferences window select *General -> Editors -> Text Editors* and here you can select a number of text display options including showing white space and configuring which caharature of those to include.
