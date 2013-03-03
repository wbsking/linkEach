import socket
import threading
import time

import logging
logging.basicConfig()

import consts
from broadcast import *

class Server(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.br_server = BroadcastServer()
        self.br_client = BroadcastClient()
        
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.settimeout(0.5)
        self.listener.bind(('', consts.SERVER_PORT))
        
    def run(self):
        self.br_client.run()
        self.br_server.run()
        while 1:
            pass
    
    
    
class Client(object):    
    def __init__(self):
        pass
    
    
    

                
if __name__ == '__main__':
    server = BroadcastServer()
    server.get_broadcast_client()
