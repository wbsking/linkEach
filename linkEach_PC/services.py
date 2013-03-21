import platform
import os
import sys
import socket

class PlatformServices(object):
    def __init__(self):
        self.local_name = self.get_local_name()
        
    def get_local_name(self):
        return '_'.join([platform.uname()[0], platform.uname()[1]])
    
    def get_local_ip(self):
        name = socket.getfqdn(socket.gethostname())
        return socket.gethostbyname(name)
    
    def shutdown(self): 
        if sys.platform.startswith('win'): 
            os.system('shutdown /s /f')
    
    def reboot(self):
        if sys.platform.startswith('win'):
            os.system('shutdown /r /f')
    
if __name__ == '__main__':
    ser = PlatformServices()
    print ser.get_local_ip()