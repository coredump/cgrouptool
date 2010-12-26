#!/usr/bin/python

import os
from debathena.metrics import connector
import threading
import fcntl

def make_non_blocking(fd):
   flags = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

class Listener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.conn = connector.Connector()
        make_non_blocking(self.conn)

    def run(self):
        while True:
            #if raw_input() == 'q':
            #    break
            #try:
                #print '.',
            ev = self.conn.recv_event()
            #except Exception, e:
            #    pass
        print ev.what

prog = Listener()
prog.start()
