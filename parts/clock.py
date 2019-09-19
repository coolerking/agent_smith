# -*- coding: utf-8 -*-

class Timestamp:
    def init(self, debug=False):
        self.debug = debug

    def run(self):
        # float
        #import time
        #return time.time()
    
        # str
        from datetime import datetime
        return str(datetime.now())


    def shutdown(self):
        pass