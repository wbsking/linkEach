import socket
import time
import threading

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
        return self._broadcast_clients.keys()
    
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
                
if __name__ == '__main__':
    client = BroadcastClient()
    client.broadcast()
    
    
    
