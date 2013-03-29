import socket
import time
import threading

from services import PlatformServices

import consts

class BroadcastClient(object):
    def __init__(self):
        self.socket = None
        self.stop_flag = False
        
    def run(self):
        br_thd = threading.Thread(target=self.broadcast)
        br_thd.setDaemon(True)
        br_thd.start()
    
    def stop_broadcast(self):
        self.stop_flag = True
    
    def broadcast(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(0.5)
        try:
            while not self.stop_flag:
                self.logger.debug("Send one broadcast packet")
                self.socket.sendto(consts.BROADCAST_MSG + PlatformServices().get_local_name(), 
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
        try:
            while not self.stop_flag:
                msg, addr = self.socket.recvfrom(consts.MAX_RECVSIZE)
                if msg[:2] == consts.BROADCAST_MSG:
                    ip = addr[0]
                    if ip != PlatformServices().get_local_ip():
                        if ip in self._broadcast_clients:
                            self._broadcast_clients[ip]['count'] = -1
                        else:
                            self._broadcast_clients[ip] = {}
                            self._broadcast_clients[ip]['count'] = -1
                            self._broadcast_clients[ip]['name'] = msg[2:]
                            
                    for ip, info_dict in self._broadcast_clients.items():
                        info_dict['count'] += 1
                        if info_dict['count'] == 2:
                            self._broadcast_clients.pop(ip)
                    
                time.sleep(3)
                
        except Exception ,ex:
            self.logger.error('%s' % ex)
            
        finally:
            self.socket.close()
            self.socket = None

class Server(object):
    def __init__(self):
        self.stop_flag = False
        
        self.services = PlatformServices()
        
        self.conn_clients = set()
        
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.settimeout(2)
        self.listener.bind(('', consts.SERVER_PORT))
        self.listener.listen(5)
    
    def stop(self):
        self.stop_flag = True
    
    def run(self):
        thd = threading.Thread(target=self._run)
        thd.start()
        
    def _run(self):
        while not self.stop_flag:
            try:
                sock, addr = self.listener.accept()
            except socket.timeout:
                continue
            self.conn_clients.add(sock)
            self.accept_method(sock)
            
    def accept_method(self, sock):
        thd = threading.Thread(target=self._serve_client, args=(sock,))
        thd.setDaemon(True)
        thd.start()
    
    def _serve_client(self, sock):
        while 1:
            try:
                data = sock.recv(consts.MAX_RECVSIZE)
            except:
                time.sleep(3)
                continue
            self._dispatch_request(sock, data)
    
    def _dispatch_request(self, sock, data):
        msg = data[:2]
        if msg == consts.GETNAME_MSG:
            name = self.services.get_local_name()
            self.send_reply(sock, consts.REPLY_OKMSG+name)
        if msg == consts.SHUTDOWN_MSG:
            self.send_reply(sock, consts.REPLY_OKMSG)
            self.services.shutdown()
        if msg == consts.REBOOT_MSG:
            self.send_reply(sock, consts.REPLY_OKMSG)
            self.services.reboot()
            
    def send_reply(self, sock, msg):
        sock.send(msg)

class Client(object):
    def __init__(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self, server_ip, server_port=consts.SERVER_PORT):
        self.conn.connect((server_ip, server_port))
    
    def close(self):
        self.conn.close()
        
    def send_msg(self, msg):
        self.conn.send(msg)
    
    def recv_msg(self):
        return self.conn.recv(consts.MAX_RECVSIZE)
    
if __name__ == '__main__':
    server = Server()
    server.run()
    
    
    
