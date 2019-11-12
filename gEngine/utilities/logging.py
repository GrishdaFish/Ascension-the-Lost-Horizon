import os
import sys
import logging

class log_manager:
    def __init__(self):
        self.log = logging.getLogger('main')
        self.log.setLevel(logging.DEBUG)
        # for py2exe, cant create a path in the libray.zip file
        path = os.path.join(sys.path[0] ,'debug')
        # path = path.replace('library.zip','')
        path = path.replace('core.exe' ,'')
        if not os.path.exists(path):
            os.makedirs(path)
            open(os.path.join(path ,'debug.txt') ,'w').close()
            open(os.path.join(path ,'error.txt') ,'w').close()
            open(os.path.join(path ,'info.txt') ,'w').close()


        formatter = logging.Formatter \
            ("[%(asctime)s] - %(name)s.%(levelname)s - [%(module)s.%(funcName)s():%(lineno)d] - %(message)s")

        file_path = os.path.join(path ,'debug.txt')
        handler = logging.FileHandler(file_path ,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        self.log.addHandler(handler)

        file_path = os.path.join(path ,'error.txt')
        handler = logging.FileHandler(file_path ,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)
        self.log.addHandler(handler)

        file_path = os.path.join(path ,'info.txt')
        handler = logging.FileHandler(file_path ,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self.log.addHandler(handler)