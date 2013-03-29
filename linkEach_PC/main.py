#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys

from broadcast import *
from Queue import Queue

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
        self.stop_flag = True


class clientThd(QtCore.QThread):
    def __init__(self, sock, remote_ip, parent=None):
        super(clientThd, self).__init__(parent)
        self.sock = sock
        self.remote_ip = remote_ip
        
    def run(self):
        try:
            self.sock.connect(self.remote_ip)
            self.emit(QtCore.SIGNAL('connected'),  self.sock, self.remote_ip)
        except Exception, ex:
            self.emit(QtCore.SIGNAL('connected'), ex)

class sendMsgThd(QtCore.QThread):
    def __init__(self, sock, msg, parent=None):
        super(sendMsgThd, self).__init__(parent)
        self.msg = msg
        self.sock = sock
        
    def run(self):
        try:
            self.sock.send_msg(self.msg)
            reply = self.sock.recv_msg()
            if reply[:2] == consts.REPLY_OKMSG:
                self.emit(QtCore.SIGNAL('reply_msg'), 'Send Message Successfully!')
        except Exception, ex:
            self.emit(QtCore.SIGNAL('reply_msg'), 'Send Message failed!')

class loadingLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(loadingLabel, self).__init__(parent)
        
        self.setFixedSize(300, 400)
        mv = QtGui.QMovie('icon/loading.gif')
        self.setMovie(mv)
        mv.start()
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setStyleSheet("background-color:rgba(200, 200, 200, 90%);")
    
    def label_show(self):
        self.show()
        self.raise_()
    
    def label_hide(self):
        if not self.isHidden():
            self.hide()
            self.lower()

class clickedLabel(QtGui.QLabel):
    def __init__(self, name, parent, default_style_sheet=None):
        super(clickedLabel, self).__init__(name, parent)
        if default_style_sheet is None:
            default_style_sheet = "background-color:rgb(100, 100, 100);"
            
        self.default_style_sheet = default_style_sheet
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
    def enterEvent(self, event):
        self.setStyleSheet("background-color:rgb(120, 120, 120);")
    
    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)
    
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color:rgb(200, 200, 200);")
        self.emit(QtCore.SIGNAL('clicked()'))
        
    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)

class castLabel(clickedLabel):
    def __init__(self, name, parent, style_sheet=None):
        super(castLabel, self).__init__(name, parent)
        
        self.remote_ip = name
        if not style_sheet:
            style_sheet = "background-color:rgb(180, 180, 180);"
        self.default_style_sheet = style_sheet
        self.setFrameShape(QtGui.QFrame.StyledPanel)
    
    def mousePressEvent(self, event):
        self.emit(QtCore.SIGNAL('cast_connect'), self.remote_ip)


class operationLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(operationLabel, self).__init__(parent)
        
        h_layout = QtGui.QHBoxLayout()
        default_style_sheet = "background-color:rgb(170, 170, 170);"\
                              "border-radius:5px;border:1px solid gray"
                              
        self.shutdown_label = radiusLabel('Shutdown', consts.SHUTDOWN_MSG, default_style_sheet, self)
        self.shutdown_label.setStyleSheet(default_style_sheet)
        self.reboot_label = radiusLabel('Reboot',  consts.REBOOT_MSG, default_style_sheet, self)
        self.reboot_label.setStyleSheet(default_style_sheet)
        
        h_layout.addWidget(self.shutdown_label)
        h_layout.addWidget(self.reboot_label)
        self.setLayout(h_layout)

class radiusLabel(QtGui.QLabel):
    def __init__(self, name, msg,  style_sheet=None, parent=None):
        super(radiusLabel, self).__init__(parent)
    
        self.msg = msg
        
        if style_sheet is None:
            style_sheet = " background-color:rgb(170, 170, 170);"\
                          "border-radius:5px;border:1px solid gray"
        self.setText(name)
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.default_style_sheet = style_sheet
    
    def enterEvent(self, event):
        self.setStyleSheet("background-color:rgb(120, 120, 120);"
                           "border-radius:5px;border:1px solid gray")
    
    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)
    
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color:rgb(200, 200, 200);"
                           "border-radius:5px;border:1px solid gray")
        self.emit(QtCore.SIGNAL('send_msg'), self.msg)
        
        
    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.default_style_sheet)

class TrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, frame):
        super(TrayIcon, self).__init__()
        
        self.setIcon(QtGui.QIcon('icon/medium.ico'))
        self.frame = frame
        
        self.tray_menu = QtGui.QMenu()
        exit_action = QtGui.QAction('Exit', self)
        show_action = QtGui.QAction('Show', self)
        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(exit_action)
        
        self.setContextMenu(self.tray_menu)
        self.activated.connect(self.onTrayClick)
        
        self.connect(exit_action, QtCore.SIGNAL('triggered()'), self.exit)
        self.connect(show_action, QtCore.SIGNAL('triggered()'), self.show_frame)
        
    def exit(self):
        self.frame.stop()
        sys.exit(0)
        
    def show_frame(self):
        if self.frame.isHidden():
            self.frame.show()
            self.frame.setWindowState(QtCore.Qt.WindowActive)
        self.frame.raise_()
    
    def onTrayClick(self, event):
        if event in (QtGui.QSystemTrayIcon.DoubleClick,):
            self.show_frame()
        
        elif event is QtGui.QSystemTrayIcon.Trigger:
            self.tray_menu.show()
                
class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.br_client = BroadcastClient()
        self.br_server = BroadcastServer()
        self.link_server = Server()

        self.check_thread = CheckBroadcast(self.br_server)
        self.connect(self.check_thread, QtCore.SIGNAL('newClient'), self.check_new_server)
        
        self.remote_server = RemoteServerList()
        
        self.setFixedSize(300, 400)
        self.setWindowTitle('linkEach')
        self.setWindowIcon(QtGui.QIcon('icon/medium.ico'))
        self.set_center()
        
        
        self.loading_label = loadingLabel(self)
        self.loading_label.show()
        
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        
        self.run()
    
    def check_new_server(self, remote_servers):
        if remote_servers:
            self.loading_label.label_hide()
        for ip, info_dict in remote_servers.items():
            for server in self.remote_server:
                if ip in server:
                    break
            else:
                self.add_cast_label(ip, info_dict)
        
        for item in self.remote_server:
            for ip in item:
                if not remote_servers.get(ip):
                    self.remove_cast_label(ip)
        if not self.remote_server and self.loading_label.isHidden():
            self.loading_label.label_show()
        
    def remove_cast_label(self, ip):
        self.group_ani = QtCore.QParallelAnimationGroup()
        
        index = self.remote_server.get_index(ip)
        self.remote_server[ip]['label'].hide()
        if self.remote_server[ip].get('operation_label'):
            self.remote_server[ip]['operation_label'].hide()
            
        for item in self.remote_server[index+1:]:
            for ip in item:
                top = item[ip]['label'].geometry().top()
                ani = QtCore.QPropertyAnimation(item[ip]['label'], 'geometry')
                ani.setStartValue(QtCore.QRect(0, top, 300, 50))
                ani.setEndValue(QtCore.QRect(0, top-50, 300, 50))
                self.group_ani.addAnimation(ani)
                
                if self.remote_server[ip].get('show_flag'):
                    ani = QtCore.QPropertyAnimation(self.remote_server[ip]['operation_label'], 'geometry')
                    tmp_top = self.remote_server[ip]['operation_label'].geometry().top()
                    ani.setDuration(300)
                    ani.setStartValue(QtCore.QRect(0, tmp_top, 300, 50))
                    ani.setEndValue(QtCore.QRect(0, tmp_top-50, 300, 50))
                    self.group_ani.addAnimation(ani)
        
        self.group_ani.start()
        del self.remote_server[index]
        
    def set_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def add_cast_label(self, remote_ip, info_dict):
        info_dict = info_dict.copy()
        label = castLabel(remote_ip, self)
        label.setStyleSheet("background-color:rgb(180,180,180)")
        
        self.connect(label, QtCore.SIGNAL('cast_connect'), self.connect_remote_server)
        label.show()
        
        self.ani = QtCore.QPropertyAnimation(label, 'geometry')
        self.ani.setDuration(500)
        if not self.remote_server:
            top = 0
        elif self.remote_server[-1].get('show_flag'):
            top = self.remote_server[-1]['operation_label'].geometry().top() + \
                   self.remote_server[-1]['operation_label'].geometry().height()
        else:
            top = self.remote_server[-1]['label'].geometry().top() + \
                        self.remote_server[-1]['label'].geometry().height() 
        self.ani.setStartValue(QtCore.QRect(300, top, 300, 50))
        self.ani.setEndValue(QtCore.QRect(0, top, 300, 50))
        self.ani.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self.ani.start()
        info_dict['label'] = label
        self.remote_server.add({remote_ip:info_dict})
        
    def connect_remote_server(self, remote_ip):
        if not self.remote_server[remote_ip].get('client'): 
            client = Client()
            self.client_thd = clientThd(client, remote_ip)
            self.client_thd.start()
            
            self.connect(self.client_thd, QtCore.SIGNAL('connected'), self.check_conn)
            
        else:
            operation_label = self.remote_server[remote_ip]['operation_label']
            if self.remote_server[remote_ip]['show_flag']:
                self.hide_operation_label(remote_ip, operation_label)
                self.remote_server[remote_ip]['show_flag'] = False
            else:
                self.show_operation_label(remote_ip, operation_label)
                self.remote_server[remote_ip]['show_flag'] = True
    
    def check_conn(self, client, remote_ip=None):
        if isinstance(client, Exception):
            self.show_message_label('connect failed!')
        
        elif isinstance(client, Client):
            self.show_message_label('connect successfully!')
            self.remote_server[remote_ip]['client'] = client
        
            operation_label = operationLabel(self)
            operation_label.setStyleSheet("background-color:#C3ECEF;")
            self.connect(operation_label.shutdown_label, QtCore.SIGNAL('send_msg'),
                         lambda msg, x=self.remote_server[remote_ip]['client']: self.send_msg(msg, x))
            self.connect(operation_label.reboot_label, QtCore.SIGNAL('send_msg'),
                         lambda msg, x=self.remote_server[remote_ip]['client']: self.send_msg(msg, x))
              
            self.remote_server[remote_ip]['operation_label'] = operation_label
                  
            self.show_operation_label(remote_ip, operation_label)
            self.remote_server[remote_ip]['show_flag'] = True

    def send_msg(self, msg, sock):
        self.send_thd = sendMsgThd(sock, msg)
        self.send_thd.start()
        self.loading_label.label_show()
        self.connect(self.send_thd, QtCore.SIGNAL('reply_msg'), self.show_message_label)
    
    def show_message_label(self, msg, duration=2000):
        self.loading_label.hide()
        if not hasattr(self, 'msg_label'):
            self.msg_label = clickedLabel(msg, self)
            self.msg_label.setStyleSheet("background-color:#91CCC0;")
        self.msg_label.show()
        self.msg_label.setText(msg)
        self.msg_ani = QtCore.QPropertyAnimation(self.msg_label, 'geometry')
        self.msg_ani.setDuration(duration)
        self.msg_ani.setKeyValueAt(0, QtCore.QRect(0, 400, 300, 35))
        self.msg_ani.setKeyValueAt(0.1, QtCore.QRect(0, 365, 300, 35))
        self.msg_ani.setKeyValueAt(0.9, QtCore.QRect(0, 365, 300, 35))
        self.msg_ani.setKeyValueAt(1, QtCore.QRect(0, 400, 300, 35))
        self.msg_ani.start()
        
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
                self.remote_server[ip]['label'].setStyleSheet()
                
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
        self.hide()
        event.ignore()
        
    def stop(self):
        self.br_client.stop_broadcast()
        self.br_server.stop()
        self.link_server.stop()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wind = mainWindow()
    wind.show()
    sys.exit(app.exec_())
    
    
    