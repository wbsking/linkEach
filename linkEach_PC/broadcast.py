import socket
import logging
import time

import consts

class BroadcastClient(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.socket = None
        
    def broadcast(self):
        pass
    
    
