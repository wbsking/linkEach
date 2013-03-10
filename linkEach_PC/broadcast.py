import socket
import time
import threading

from services import PlatformServices

import logging
logging.basicConfig(level='DEBUG')

import consts

class BroadcastClient(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.socket = None
    
    def run(self):
        br_thd = threading.Thread(target=self.broadcast)
        br_thd.setDaemon(True)
        br_thd.start()
    
    def broadcast(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(0.5)
        try:
            while 1:
                self.logger.debug("Send one broadcast packet")
                self.socket.sendto(consts.BROADCAST_MSG, 
                               (consts.BROADCAST_IP, consts.BROADCAST_PORT))
                time.sleep(5)
        except Exception, ex:
            self.logger.error('%s' % ex)
        finally:
            self.socket.close()
            self.socket = None
            
class BroadcastServer(object):
    def __init__(self):
        self._broadcast_clients = {}
        self.socket = None
        self.stop_flag = False
        
    def run(self):
        br_thd = threading.Thread(target=self._get_broadcast_client)
        br_thd.setDaemon(True)
        br_thd.start()
    
    def stop(self):
        self.stop_flag = True
    
    @property
    def broadcast_clients(self):
        return self._broadcast_clients
    
    def _get_broadcast_client(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', consts.BROADCAST_PORT))
        while not self.stop_flag:
            try:
                msg, addr = self.socket.recvfrom(consts.MAX_RECVSIZE)
                if msg == consts.BROADCAST_MSG:
                    self._broadcast_clients[addr[0]] = 0
                    for ip_addr, count in self._broadcast_clients.items():
                        if count == 4:    
                            self._broadcast_clients.pop(ip_addr)
                        self._broadcast_clients[ip_addr] += 1
                        
                time.sleep(60)
            except Exception ,ex:
                self.logger.error('%s' % ex)
                raise
            
            finally:
                self.socket.close()
                self.socket = None


class Server(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.services = PlatformServices()
        
        self.conn_clients = set()
        
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.settimeout(2)
        self.listener.bind(('', consts.SERVER_PORT))
        
    def run(self):
        thd = threading.Thread(target=self._run)
        thd.start()
        
    def _run(self):
        while 1:
            try:
                sock, addr = self.listener.accept()
            except socket.timeout:
                continue
            self.conn_clients.add(sock)
            self.accept_method(sock)
            
    def _accept_method(self, sock):
        thd = threading.Thread(target=self._serve_client, args=(sock,))
        thd.setDaemon(True)
        thd.start()
    
    def _serve_client(self, sock):
        while 1:
            try:
                data = sock.recv(consts.MAX_RECVSIZE)
            except socket.timeout:
                pass
            self._dispatch_request(sock, data)
    
    def _dispatch_request(self, sock, data):
        if data == consts.GETNAME_MSG:
            name = self.services.get_local_name()
            self._send_reply(sock, name)
        if data == consts.SHUTDOWN_MSG:
            self.services.shutdown()
        if data == consts.REBOOT_MSG:
            self.services.reboot()
        if data.startswith(consts.REPLYNAME_MSG):
            print data.split(consts.REPLYNAME_MSG)[1]
            
    def _send_reply(self, sock, msg):
        sock.send(consts.REPLYNAME_MSG + msg)

class Client(object):
    def __init__(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, server_ip):
        self.conn.connect(server_ip)
        
    def send_msg(self, msg):
        self.conn.send(msg)
    
    def recv_msg(self):
        return self.conn.recv(consts.MAX_RECVSIZE)
    
if __name__ == '__main__':
    client = BroadcastClient()
    client.broadcast()
    
    
    
