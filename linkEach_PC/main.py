#!/usr/bin/python
#-*- coding:utf-8 -*-

import socket
import threading
import time

import consts
from broadcast import *

from PyQt4 import QtCore, QtGui


class RemoteServerList(list):
    def __init__(self):
        super(RemoteServerList, self).__init__()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            value_dict = super(RemoteServerList, self).__getitem__(key)
            for key, value in value_dict.items():
                return value
        
        for item in self:
            if key in item:
                return item[key]
    
    def add(self, item):
        self.append(item)
    
    def set(self, key, value):
        for item in self:
            if key in item:
                item.update({key:value})
    
    def get(self, key):
        for item in self:
            if key in item:
                return item[key]
    
    def get_index(self, key):
        for index, item in enumerate(self):
            if key in item:
                return index
            
            
            

class CheckBroadcast(QtCore.QThread):
    def __init__(self, br_server, parent=None):
        super(CheckBroadcast, self).__init__(parent)
        self.stop_flag = False
        self.br_server = br_server
        
    def run(self):
        while not self.stop_flag:
            clients = self.br_server.broadcast_clients
            self.emit(QtCore.SIGNAL('newClient'), clients)
            time.sleep(5)
    
    def stop(self):
        pass

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.br_client = BroadcastClient()
        self.br_server = BroadcastServer()
        self.link_server = Server()
        self.check_thread = CheckBroadcast(self.br_server)
        
        self.connect(self.check_thread, QtCore.SIGNAL('newClient'), self.check_new_server)
        
        self.remote_server = RemoteServerList()

        self.init()
        
    def init(self):
        self.setFixedSize(300, 400)
        self.setWindowTitle('linkEach')
        self.set_center()
        self.create_refresh_wdiget()
        
        self.run()
        
    def check_new_server(self, remote_servers):
        for ip, info_dict in remote_servers.items():
            for server in self.remote_server:
                if ip in server:
                    break
            else:
                self.add_cast_label(ip, info_dict)
    
    #TODO:
    def remove_cast_label(self, ip):
        pass
    
    def set_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def add_cast_label(self, remote_ip, info_dict):
        cast_abel_style_sheet = "background-color:rgb(220, 220, 220);"
        label = castLabel(remote_ip, self, cast_abel_style_sheet)
        self.connect(label, QtCore.SIGNAL('connect'), self.connect_remote_server)
        label.show()
        
        self.ani = QtCore.QPropertyAnimation(label, 'geometry')
        self.ani.setDuration(500)
        if not self.remote_server:
            top = 0
        elif self.remote_server[-1].get('show_flag'):
            top = self.remote_server[-1]['operation_label'].geometry().top() + self.remote_server[-1]['operation_label'].geometry().height()
        else:
            top = self.remote_server[-1]['label'].geometry().top() + self.remote_server[-1]['label'].geometry().height() 
        self.ani.setStartValue(QtCore.QRect(300, top, 300, 50))
        self.ani.setEndValue(QtCore.QRect(0, top, 300, 50))
        self.ani.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self.ani.start()
        info_dict['label'] = label
        self.remote_server.add({remote_ip:info_dict})
        
    def create_refresh_wdiget(self):
        self.refresh_label = clickedLabel('SCAN', self)
        self.refresh_label.setGeometry(0, 350, 300, 50)
        self.connect(self.refresh_label, QtCore.SIGNAL('clicked'), self.rescan)
    
    def rescan(self):
        pass
    
    #TODO: connect will frozen the UI
    def connect_remote_server(self, remote_ip):
        try:
            if not self.remote_server[remote_ip].get('client'): 
                client = Client()
                client.connect(remote_ip)
                self.remote_server[remote_ip]['client'] = client
                operation_label = operationLabel(self)
                self.remote_server[remote_ip]['show_flag'] = False
                self.remote_server[remote_ip]['operation_label'] = operation_label
            else:
                operation_label = self.remote_server[remote_ip]['operation_label']
                
            if not self.remote_server[remote_ip].get('show_flag'):
                self.show_operation_label(remote_ip, operation_label)
                self.remote_server[remote_ip]['show_flag'] = True
            else:
                self.hide_operation_label(remote_ip, operation_label)
                self.remote_server[remote_ip]['show_flag'] = False
            
        except Exception, ex:
            print ex
    
    def hide_operation_label(self, remote_ip, operation_label):
        self.group_ani = QtCore.QParallelAnimationGroup()
        
        index = self.remote_server.get_index(remote_ip)
        for item in self.remote_server[index+1:]:
            for ip in item:
                tmp_top = self.remote_server[ip]['label'].geometry().top()
                ani = QtCore.QPropertyAnimation(self.remote_server[ip]['label'], 'geometry')
                ani.setDuration(300)
                ani.setStartValue(QtCore.QRect(0, tmp_top, 300, 50))
                ani.setEndValue(QtCore.QRect(0, tmp_top-50, 300, 50))
                self.group_ani.addAnimation(ani)
                
                if self.remote_server[ip]['show_flag']:
                    ani = QtCore.QPropertyAnimation(self.remote_server[ip]['operation_label'], 'geometry')
                    tmp_top = self.remote_server[ip]['operation_label'].geometry().top()
                    ani.setDuration(300)
                    ani.setStartValue(QtCore.QRect(0, tmp_top, 300, 50))
                    ani.setEndValue(QtCore.QRect(0, tmp_top-50, 300, 50))
                    self.group_ani.addAnimation(ani)
            
        ani = QtCore.QPropertyAnimation(operation_label, 'geometry')
        ani.setDuration(300)
        top = operation_label.geometry().top()
        ani.setStartValue(QtCore.QRect(0, top, 300, 50))
        ani.setEndValue(QtCore.QRect(0, top, 300, 0))
        self.group_ani.addAnimation(ani)
        self.group_ani.start()
        
    
    def show_operation_label(self, remote_ip, operation_label):
        self.group_ani = QtCore.QParallelAnimationGroup()
        
        remote_info = self.remote_server.get(remote_ip) 
        top = remote_info['label'].geometry().top()
        index = self.remote_server.get_index(remote_ip)
        
        for item in self.remote_server[index+1:]:
            for ip in item:
                tmp_top = self.remote_server[ip]['label'].geometry().top()
                ani = QtCore.QPropertyAnimation(self.remote_server[ip]['label'], 'geometry')
                ani.setDuration(300)
                ani.setStartValue(QtCore.QRect(0, tmp_top, 300, 50))
                ani.setEndValue(QtCore.QRect(0, tmp_top+50, 300, 50))
                self.group_ani.addAnimation(ani)
                if self.remote_server[ip]['show_flag']:
                    ani = QtCore.QPropertyAnimation(self.remote_server[ip]['operation_label'], 'geometry')
                    tmp_top = self.remote_server[ip]['operation_label'].geometry().top()
                    ani.setDuration(300)
                    ani.setStartValue(QtCore.QRect(0, tmp_top, 300, 50))
                    ani.setEndValue(QtCore.QRect(0, tmp_top+50, 300, 50))
                    self.group_ani.addAnimation(ani)
         
        operation_label.show()
        ani = QtCore.QPropertyAnimation(operation_label, 'geometry')
        ani.setDuration(300)
        ani.setStartValue(QtCore.QRect(0, top+50, 300, 0))
        ani.setEndValue(QtCore.QRect(0, top+50, 300, 50))
        self.group_ani.addAnimation(ani)
         
        self.group_ani.start()
        
     
    
    def run(self):
        self.br_client.run()
        self.br_server.run()
        self.link_server.run()
        self.check_thread.start()
        
    def closeEvent(self, event):
        self.br_client.stop_broadcast()
        self.br_server.stop()
        self.link_server.stop()

class clickedLabel(QtGui.QLabel):
    def __init__(self, name, parent, default_style_sheet=None):
        super(clickedLabel, self).__init__(name, parent)
        if default_style_sheet is None:
            default_style_sheet = "background-color:rgb(100, 100, 100);"
            
        self.default_style_sheet = default_style_sheet
        self.setStyleSheet(self.default_style_sheet)
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
    def enterEvent(self, event):
        self.setStyleSheet("background-color:rgb(120, 120, 120);")
    
    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)
    
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color:rgb(200, 200, 200);")
        self.emit(QtCore.SIGNAL('clicked'))
        
    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)

class castLabel(clickedLabel):
    def __init__(self, name, parent, default_style_sheet=None):
        super(castLabel, self).__init__(name, parent)
        
        self.name = name
        if default_style_sheet is None:
            default_style_sheet = "background-color:rgb(180, 180, 180);"
        
        self.default_style_sheet = default_style_sheet
        self.setStyleSheet(self.default_style_sheet)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setStyleSheet("border:1px solid gray;")
    
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color:rgb(200, 200, 200);")
        self.emit(QtCore.SIGNAL('connect'), self.name)


class operationLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(operationLabel, self).__init__(parent)
        
        self.setStyleSheet("background-color:rgb(100, 100, 100);")
        self.setStyleSheet("border:1px solid gray;")
        
        h_layout = QtGui.QHBoxLayout()
        default_style_sheet = "background-color:rgb(170, 170, 170);"
        self.shutdown_label = clickedLabel('Shutdown', self, default_style_sheet)
        self.shutdown_label.setStyleSheet("border-radius:2px;border:1px solid gray")
        self.reboot_label = clickedLabel('Reboot', self, default_style_sheet)
        self.reboot_label.setStyleSheet("border-radius:2px;border:1px solid gray")
        
        h_layout.addWidget(self.shutdown_label)
        h_layout.addWidget(self.reboot_label)
        self.setLayout(h_layout)
        

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    wind = mainWindow()
    wind.show()
    sys.exit(app.exec_())
    
    
    