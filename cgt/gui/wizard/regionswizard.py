"""
Created on Mon 08 Feb 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
import PyQt5.QtWidgets as qw

from cgt.gui.wizard.regionswizardpages import RegionsWizardPages as rwp
from cgt.gui.wizard.regionswizardstartpage import RegionsWizardStartPage
from cgt.gui.wizard.regionswizardcheckpage import RegionsWizardCheckPage
from cgt.gui.wizard.regionswizardfinalpage import RegionsWizardFinalPage

class RegionsWizard(qw.QWizard):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # ensure we have a "Back" button
        self.setWizardStyle(qw.QWizard.ClassicStyle)
        
        # the pages are not interdepenent and the start page has no back button
        self.setOptions(qw.QWizard.IndependentPages|qw.QWizard.NoBackButtonOnStartPage)
        
        # set up the pages
        self.setPage(rwp.PAGE_START, RegionsWizardStartPage(self))
        self.setPage(rwp.PAGE_CHECK, RegionsWizardCheckPage(self))
        self.setPage(rwp.PAGE_FINAL, RegionsWizardFinalPage(self))
        
        # make sure the start page is set
        self.setStartId(rwp.PAGE_START)
        
        self.setWindowTitle(self.tr("CGT Region Selection"))
        
    def accept(self):
        """
        action when the user clicks "Finished"
        """
        
        print(f"Editing finished")
