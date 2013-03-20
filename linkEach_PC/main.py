#!/usr/bin/python
#-*- coding:utf-8 -*-

import socket
import threading
import time

import consts
from broadcast import *

from PyQt4 import QtCore, QtGui



class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.cast_labels = []
        self.br_client = BroadcastClient()
        self.br_server = BroadcastServer()
        self.link_server = Server()
        self.clients = []
        self.stop_check_flag = False
        
        self.init()
        
    def init(self):
        self.setFixedSize(300, 400)
        self.setWindowTitle('linkEach')
        self.set_center()
        self.create_refresh_wdiget()
        
        self.run()
    
    def get_broadcast_client(self):
        thd = threading.Thread(target=self._get_broadcast_client)
        thd.setDaemon(True)
        thd.start()
    
    def _get_broadcast_client(self):
        while not self.stop_check_flag:
            clients = self.br_server.broadcast_clients
            print clients
            time.sleep(5)
    
    def set_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def add_cast_label(self, name):
        cast_abel_style_sheet = "background-color:rgb(220, 220, 220);"
        label = clickedLabel(name, self, cast_abel_style_sheet)
        label.setFrameShape(QtGui.QFrame.StyledPanel)
        label.setGeometry(QtCore.QRect(0, 0, 300, 50))
        label.setStyleSheet("border:1px solid gray;")
        label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label.show()
        
        self.ani = QtCore.QPropertyAnimation(label, 'geometry')
        self.ani.setDuration(500)
        self.ani.setStartValue(QtCore.QRect(300, 50*len(self.cast_labels), 300, 50))
        self.ani.setEndValue(QtCore.QRect(0, 50*len(self.cast_labels), 300, 50))
        self.ani.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self.ani.start()
        self.cast_labels.append(label)
        
    def create_refresh_wdiget(self):
        self.refresh_label = clickedLabel('SCAN', self)
        self.refresh_label.setGeometry(0, 350, 300, 50)
        self.connect(self.refresh_label, QtCore.SIGNAL('clicked'), self.rescan)
    
    def rescan(self):
        pass
    
    def run(self):
        self.br_client.run()
        self.br_server.run()
        self.link_server.run()
        self.get_broadcast_client()
        
    def closeEvent(self, event):
        self.br_client.stop_broadcast()
        self.br_server.stop()
        self.link_server.stop()
    
class clickedLabel(QtGui.QLabel):
    def __init__(self, name, parent, default_style_sheet=None):
        super(clickedLabel, self).__init__(name, parent)
        if default_style_sheet is None:
            default_style_sheet = "background-color:rgb(100, 100, 100)"
            
        self.default_style_sheet = default_style_sheet
        self.setStyleSheet(self.default_style_sheet)
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
    def enterEvent(self, event):
        self.setStyleSheet("background-color:rgb(120, 120, 120)")
    
    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)
    
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color:rgb(200, 200, 200)")
        self.emit(QtCore.SIGNAL('clicked'))
        
    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)
    
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    wind = mainWindow()
    wind.show()
    sys.exit(app.exec_())
    
    
    