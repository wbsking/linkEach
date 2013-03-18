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
        
        self.create_refresh_wdiget()
        self.setStyleSheet("background-color:#00ff00")
    
    def set_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    
    def add_cast_label(self, name):
        label = QtGui.QLabel(name, self)
        label.setFrameShape(QtGui.QFrame.StyledPanel)
        label.setStyleSheet("background-color:rgb(200, 200, 200);"
                            "border:1px solid gray;")
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.ani = QtCore.QPropertyAnimation(label, 'geometry')
        self.ani.setDuration(500)
        self.ani.setStartValue(QtCore.QRect(0, 400, 300, 50))
        self.ani.setEndValue(QtCore.QRect(0, 50*len(self.cast_labels), 300, 50))
        self.cast_labels.append(label)
        self.ani.start()
        
        
    def create_refresh_wdiget(self):
        self.refresh_label = clickedLabel('Scan', self)
        self.refresh_label.setGeometry(0, 350, 300, 50)
    

class clickedLabel(QtGui.QLabel):
    def __init__(self, name, parent):
        super(clickedLabel, self).__init__(name, parent)
        
        self.setStyleSheet("background-color:rgb(150, 150, 150)")
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
    def mouseMoveEvent(self, event):
        pass
        
    def mousePressEvent(self, event):
        pass
    
    def mouseReleaseEvent(self, event):
        pass
    
    
        

    
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    wind = mainWindow()
    wind.show()
    sys.exit(app.exec_())
    
    
    