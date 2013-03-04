import socket
import threading
import time

import logging
logging.basicConfig()

import consts
from broadcast import *
from services import PlatformServices

class Server(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.br_server = BroadcastServer()
        self.br_client = BroadcastClient()
        
        self.services = PlatformServices()
        
        self.clients = set()
        
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.settimeout(0.5)
        self.listener.bind(('', consts.SERVER_PORT))
        
    def run(self):
        while 1:
            try:
                sock, addr = self.listener.accept()
            except socket.timeout:
                pass
            self.clients.add(sock)
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

                
if __name__ == '__main__':
    server = BroadcastServer()
    server.get_broadcast_client()