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
from ConfigParser import ConfigParser
from libcgrouptool.skel import Cgroup, CgroupError

current_dir = os.path.dirname(os.path.realpath(__file__))
config_locations = [current_dir, '/etc/']
config_name = 'cgrouptoold.cfg'

config = ConfigParser()
result = config.read([path.join(x, config_name) for x in config_locations])
if len(result) < 1:
    raise CgroupError("Error reading config file")
