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
from os import path
from ConfigParser import ConfigParser, NoOptionError
from libcgrouptool.skel import Cgroup, CgroupError

class CgroupToolDaemonError(Exception):
    def __init__(self, value):
        self.value = value

    def str(self, value):
        return repr(value)

class CgroupToolDaemon:

    def __init__(self):
        pass

    def parse_config(self):
        current_dir = os.getcwd()
        config_locations = [current_dir, '/etc/']
        print config_locations
        config_name = 'cgrouptoold.cfg'
        self.config = ConfigParser()
        result = self.config.read([path.join(dirs, config_name) for dirs
                                                in config_locations])
        if len(result) < 1:
            raise CgroupError("Error reading config file")

        self.enabled_engines = []
        try:
            for section in self.config.sections():
                if section == 'Common':
                    continue
                if self.config.get(section, 'Enabled') == 'True':
                    self.enabled_engines.append(section)

            self.loglevel = self.config.get('Common', 'LogLevel')
            self.logfile = self.config.get('Common', 'LogFile')
            self.logfacility = self.config.get('Common', 'LogFacility')
            self.logdest = self.config.get('Common', 'LogDestination')
        except NoOptionError:
            raise CgroupToolDaemonError("All options must be present on the cfg file")

        if len(self.enabled_engines) > 1:
            raise CgroupToolDaemonError("Only one engine can be enabled")
