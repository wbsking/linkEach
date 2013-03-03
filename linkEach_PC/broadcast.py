import socket
import time

import logging
logging.basicConfig(level='DEBUG')

import consts

class BroadcastClient(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.socket = None
        
    def broadcast(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(0.5)
        try:
            while 1:
                self.logger.debug("Send one broadcast packet")
                self.socket.sendto(consts.BROADCAST_MSG, 
                               (consts.BROADCAST_IP, consts.BROADCAST_PORT))
                time.sleep(60)
        except Exception, ex:
            self.logger.error('%s' % ex)
        finally:
            self.socket.close()
            self.socket = None

if __name__ == '__main__':
    client = BroadcastClient()
    client.broadcast()
    
    
    
