#!/usr/bin/python

import os
from debathena.metrics import connector
import threading
import fcntl

def make_non_blocking(fd):
   flags = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

conn = connector.Connector()
#make_non_blocking(conn)

while True:
    try:
        ev = conn.recv_event()
    except Exception, e:
        print e

    if ev.what == connector.PROC_EVENT_FORK:
        linkpath = os.path.join('/proc/', str(ev.child_pid), 'exe')
        name = os.readlink(linkpath)
        print "Parent: ", ev.parent_pid, "Forked: ", ev.child_pid, name
    elif ev.what == connector.PROC_EVENT_EXEC:
        linkpath = os.path.join('/proc/', str(ev.process_pid), 'exe')
        name = os.readlink(linkpath)
        print "Exec: ", ev.process_pid, name
    elif ev.what == connector.PROC_EVENT_EXIT:
        linkpath = os.path.join('/proc', str(ev.process_pid), 'exe')
        if os.path.exists(linkpath):
            name = os.readlink(linkpath)
        else:
            name = None
        print "Exit: ", ev.process_pid, name
