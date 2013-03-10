#!/usr/bin/python
#-*- coding:utf-8 -*-

import socket
import threading
import time

import logging
logging.basicConfig()

import consts
from broadcast import *

from PyQt4 import QtCore, QtGui

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.cast_labels = []
        self.init()
        
    def init(self):
        self.setFixedSize(300, 400)
        self.setWindowTitle('linkEach')
        self.set_center()
        
        self.create_cast_group_layout()
        self.setLayout(self.cast_group_layout)
        self.create_refresh_wdiget()
        self.setStyleSheet("background-color:#00ff00")
        self.show()
    
    def set_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    
    def create_cast_group_layout(self):
        self.cast_group_layout = QtGui.QGridLayout()
        
    def add_cast_label(self, name):
        label = QtGui.QLabel(name)
        
    def create_refresh_wdiget(self):
        self.refresh_label = QtGui.QLabel('Refresh', self)
        self.refresh_label.setStyleSheet("background-color:#0000ff")
        self.refresh_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.refresh_label.setGeometry(0, 350, 300, 50)
        
          
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    wind = mainWindow()
    sys.exit(app.exec_())
    
    
    