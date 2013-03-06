import platform
import os
import sys

class PlatformServices(object):
    def __init__(self):
        self.local_name = self.get_local_name()
        
    def get_local_name(self):
        return '_'.join([platform.uname()[0], platform.uname()[1]])
    
    def shutdown(self): 
        if sys.platform.startswith('win'): 
            os.system('shutdown /s')
    
    def reboot(self):
        if sys.platform.startswith('win'):
            os.system('shutdown /r')
    
if __name__ == '__main__':
    pass