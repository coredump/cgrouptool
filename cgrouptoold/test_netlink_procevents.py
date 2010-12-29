#!/usr/bin/python

import os
import fcntl
import select
from select import poll
from debathena.metrics import connector
from threading import Thread

def make_non_blocking(fd):
   flags = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

#make_non_blocking(conn)


class Listener(Thread):

    def __init__(self):
        Thread.__init__(self)
        try:
            self.conn = connector.Connector()
            make_non_blocking(self.conn)
            self.polling = poll()
            poll_mask = (select.POLLIN | select.POLLPRI | select.POLLERR )
            self.polling.register(self.conn, poll_mask)
        except IOError, e:
            print "Must be root: %s" % e
            os._exit(2)

    def run(self):
        while True:
            try:
                p_result = self.polling.poll()
                print p_result
                if p_result[0][1] <= select.POLLPRI:
                    self.ev = self.conn.recv_event()
                else:
                    continue
            except Exception, e:
                print e

            if self.ev.what == connector.PROC_EVENT_FORK:
                linkpath = os.path.join('/proc/', str(self.ev.child_pid), 'exe')
                if os.path.exists(linkpath):
                    name = os.readlink(linkpath)
                else:
                    name = 'non ecsiste'
                print "Parent: ", self.ev.parent_pid, "Forked: ", self.ev.child_pid, name
            elif self.ev.what == connector.PROC_EVENT_EXEC:
                linkpath = os.path.join('/proc/', str(self.ev.process_pid), 'exe')
                name = os.readlink(linkpath)
                print "Exec: ", self.ev.process_pid, name
            elif self.ev.what == connector.PROC_EVENT_EXIT:
                linkpath = os.path.join('/proc', str(self.ev.process_pid), 'exe')
                if os.path.exists(linkpath):
                    name = os.readlink(linkpath)
                else:
                    name = None
                print "Exit: ", self.ev.process_pid, name

if __name__ == '__main__':
    prog = Listener()
    prog.start()
