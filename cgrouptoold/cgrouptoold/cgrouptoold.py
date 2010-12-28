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
import logging
from utils import CgroupToolDaemonError
from os import path
from logging import handlers
from threading import Thread
from Queue import Queue
from debathena.metrics import connector
from ConfigParser import ConfigParser, NoOptionError
from libcgrouptool.skel import Cgroup, CgroupError
from Engines import TTY

class CgroupToolDaemon:

    def __init__(self):
        """ """

        self.queue = Queue()
        self.enabled_engines = []

        self.parse_config()
        self._setup_logging()

    def parse_config(self):
        current_dir = os.getcwd()
        config_locations = [current_dir, "/etc/"]
        config_name = "cgrouptoold.cfg"
        self.config = ConfigParser()
        result = self.config.read([path.join(dirs, config_name) for dirs
                                                in config_locations])
        if len(result) < 1:
            raise CgroupError("Error reading config file")

        try:
            for section in self.config.sections():
                if section == "Common":
                    continue
                if self.config.get(section, "Enabled") == "True":
                    self.enabled_engines.append(section)

            self.loglevel = self.config.get("Common", "LogLevel").lower()
            self.logfile = self.config.get("Common", "LogFile").lower()
            self.logfacility = self.config.get("Common", "LogFacility").lower()
            self.logdest = self.config.get("Common", "LogDestination").lower()
            self.cgroupfs = self.config.get("Common", "CgroupFsMountPoint").lower()
        except NoOptionError:
            raise CgroupToolDaemonError("All options must be present on the cfg file")

        if len(self.enabled_engines) > 1:
            raise CgroupToolDaemonError("Only one engine can be enabled")

    def start_daemon(self):
        creator = CgroupCreator(self.queue, self.log)
        listener = EventListener(self.queue, self.log)
        creator.start()
        listener.start()

    def reload_daemon(self):
        pass

    def exit_gracefully(self):
        pass

    def _setup_logging(self):
        """You can have three levels of logging on the config file: debug, 
        info or critical. The facilities can be any of those strings reflecting
        the ones listed on man syslog: 

        auth authpriv cron daemon ftp kern lpr mail news syslog user uucp 
        local0 local1 local2 local3 local4 local5 local6 local7
        """

        log_levels = { "debug" : logging.DEBUG,
                       "info"  : logging.INFO,
                       "critical" : logging.CRITICAL,
                     }

        logger = logging.getLogger("cgrouptoold")
        logger.setLevel(log_levels[self.loglevel])

        if self.logdest == "file":
            handler = logging.FileHandler(self.logfile)
            handler.setLevel(log_levels[self.loglevel])
        elif self.logdest == "syslog":
            print 'using syslog'
            handler = handlers.SysLogHandler('/dev/log', self.logfacility)
            handler.setLevel(log_levels[self.loglevel])
        else:
            raise CgroupToolDaemonError("Incorrect LogFacility config")

        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_str)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.log = logger
        self.debug = logger.debug
        self.info = logger.info
        self.crit = logger.critical

class EventListener(Thread):
    """Listens for netlink connector events and puts them on a queue"""

    def __init__(self, queue, log):
        Thread.__init__(self)
        self.queue = queue
        self.log = log
        self.debug, self.info, self.crit = log.debug, log.info, log.critical
        try:
            self.conn = connector.Connector()
        except IOError:
            raise CgroupToolDaemonError("This daemon must be started as root")

    def run(self):
        monitor_events = [ connector.PROC_EVENT_FORK,
                           connector.PROC_EVENT_EXEC,
                           connector.PROC_EVENT_EXIT,
                         ]
        while True:
            try:
                ev = self.conn.recv_event()
            except Exception, e:
                raise CgroupToolDaemonError("%s" % e)
            if ev.what in monitor_events:
                self.queue.put(ev)

class CgroupCreator(Thread):

    def __init__(self, queue, log):
        Thread.__init__(self)
        self.log = log
        self.debug, self.info, self.crit = log.debug, log.info, log.critical
        self.queue = queue

    def run(self):
        engine = TTY(self.log)
        while True:
            ev = self.queue.get()
            if ev.what == connector.PROC_EVENT_EXEC:
                engine.new_exec(ev.process_pid)
            elif ev.what == connector.PROC_EVENT_EXIT:
                engine.new_exit(ev.process_pid)
            self.queue.task_done()
