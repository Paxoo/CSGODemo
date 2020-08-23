# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 20:26:05 2020

@author: Pati
"""

import sys
#from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction, QFileDialog, QMessageBox
#from PyQt5.QtWidgets import QDesktopWidget

from csgo.parser import DemoParser
from showStatistics import showStatistic

import PyQt5.QtWidgets as QtWidgets

    
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.setWindowTitle("CSGO Demo Analyzer")
        self.setGeometry(300, 200, 640, 640)
        
        # move Window to center
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        self.demofile = ""
        self.data = []
        self.guard_demoLoaded = False

        self.init_menubar()
        
    def init_menubar(self):
        # Create openfile action
        openfileAction = QtWidgets.QAction('&Open demo file', self)        
        openfileAction.setStatusTip('You know')
        openfileAction.triggered.connect(self.openFileNameDialog)
        
        # Create contact action
        contactAction = QtWidgets.QAction('&Contact', self)        
        contactAction.setStatusTip('Its me')
        contactAction.triggered.connect(self.openContact)
        
        # Create statistic actions
        showKDRAction = QtWidgets.QAction('&Show final KDR', self)        
        showKDRAction.setStatusTip('ya boy')
        showKDRAction.triggered.connect(self.showKDR)
        
        showUtilityDMGAction = QtWidgets.QAction('&Show final Utility DMG', self)        
        showUtilityDMGAction.setStatusTip('damage')
        showUtilityDMGAction.triggered.connect(self.showUtilityDMG)
        
        showEFAction = QtWidgets.QAction('&Show final EnemiesFlashed', self)        
        showEFAction.setStatusTip('cant see')
        showEFAction.triggered.connect(self.showEF)
        
        showTFAction = QtWidgets.QAction('&Show final TeamFlashes', self)        
        showTFAction.setStatusTip('cant see')
        showTFAction.triggered.connect(self.showTF)

        # Create menu bar and add action
        mainMenu = QtWidgets.QMenuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openfileAction)
        
        statisticMenu = mainMenu.addMenu('&Statistic')
        statisticMenu.addAction(showKDRAction)
        statisticMenu.addAction(showUtilityDMGAction)
        statisticMenu.addAction(showEFAction)
        statisticMenu.addAction(showTFAction)
        
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(contactAction)
        
        self.setMenuBar(mainMenu)
        
    def openContact(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Contact information")
        msg.setText("For questions, problems or feedback please use the git repository. In this repository, you will find the source code and issue tracker pertaining to the csgo package.")
        msg.setInformativeText('<a href="https://github.com/Paxoo/CSGODemo">Github: Paxoo CSGODemo</a>')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.exec()         
        
    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Demo Files (*.dem)", options=options)
        if fileName:
            self.demofile = fileName
            self.guard_demoLoaded = True
        
        demo_parser = DemoParser(demofile = self.demofile, match_id = "T")
        self.data = demo_parser.parse()
                 
    def showKDR(self):
        if self.guard_demoLoaded is True:
            stats = showStatistic(self.data)
            stats.show_KDR()
    
    def showUtilityDMG(self):
        if self.guard_demoLoaded is True:
            stats = showStatistic(self.data)
            stats.show_utilityDMG()
            
    def showEF(self):
        if self.guard_demoLoaded is True:
            stats = showStatistic(self.data)
            stats.show_EnemiesFlashed()
            
    def showTF(self):
        if self.guard_demoLoaded is True:
            stats = showStatistic(self.data)
            stats.show_TeamFlashes()
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())