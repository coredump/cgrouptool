#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2010 José de Paula Eufrásio Júnior <jose.junior@gmail.com>
#
# This file is part of cgrouptools.
#
# cgrouptools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cgrouptools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with cgrouptools.  If not, see <http://www.gnu.org/licenses/>.

import os
import fcntl
from debathena.metrics import connector

def make_non_blocking(fd):
   flags = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

class CgroupToolDaemonError(Exception):
    def __init__(self, value):
        self.value = value

    def str(self, value):
        return repr(value)

class Event:
    """Gets an event result from connector and encapsulates it more 
    generically"""

    def __init__(self, event):
        self.event = event
        if self.event.what == connector.PROC_EVENT_FORK:
            self.pid = None
            self.type = 'fork'
            self.path = None
        elif self.event.what == connector.PROC_EVENT_EXEC:
            linkpath = os.path.join('/proc/', str(self.event.process_pid), 'exe')
            self.pid = self.event.process_pid
            self.type = 'exec'
            try:
                self.path = os.readlink(linkpath)
            except OSError:
                # Process vanished too fast to be recorded
                self.path = None
        elif self.event.what == connector.PROC_EVENT_EXIT:
            self.pid = self.event.process_pid
            self.type = 'exit'
            self.path = None
