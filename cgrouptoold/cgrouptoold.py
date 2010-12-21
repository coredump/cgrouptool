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

# This daemon uses the implementation module of PEP 3143, python-daemon,
# that can be found on pypi and will be included on standard lib on 3.x
# It deals with daemon creating and DTRT. The PEP is a very interesting
# lecture about Unix daemon creation.

from cgrouptoold.cgrouptoold import CgroupToolDaemon
from daemon import daemon

cgtd = CgroupToolDaemon()
cgtd.parse_config()
cgtd.debug(cgtd.config.sections())
