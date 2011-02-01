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
import re
from debathena.metrics import connector
from libcgrouptool.skel import Cgroup, CgroupError
from cgrouptoold.utils import CgroupToolDaemonError, Engine

class TTY(Engine):
    """Simple engine that will create a separate cgroup for each process
    that owns a TTY/PTY
    """

    def __init__(self, log):
        Engine.__init__(self, log)

    def check_stdin(self, pid):
        """Checks if the stdin of a process is connected to a terminal file
        descriptor
        """

        fdpath = os.path.join('/proc', str(pid), 'fd/1')
        try:
            stdin = os.readlink(fdpath)
            if (stdin.find('pts') >= 0  or
                stdin.find('tty') >= 0):
                return True
            else:
                return False
        except OSError:
            raise CgroupToolDaemonError("Process vanished too fast")

    def new_exec(self, pid):
        """Receives the pid from a new exec() and decides if it should be put
        on a new cgroup. In case it does, starts the process to create the
        cgroup and organize the processes there.
        """
        self.debug("=> Inside new exec")
        name = self.resolve_name(pid)
        try:
            if self.check_stdin(pid):
                self.debug("PID %s/%s connected to terminal" % (pid, name))
            else:
                self.debug("PID %s/%s NOT connected to a terminal" % (pid, name))
        except CgroupToolDaemonError:
            # Expected in case process vanish too fast, just ignore them
            self.debug("Process %s vanished too fast" % pid)
            pass

    def new_exit(self, pid):
        """docstring for exit"""
        self.debug("PID %s exited" % pid)
