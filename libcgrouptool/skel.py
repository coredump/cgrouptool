#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2010 José de Paula Eufrásio Júnior <jose.junior@gmail.com>
#
# This file is part of libcgrouptools.
#
# libcgrouptools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libcgrouptools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with libcgrouptools.  If not, see <http://www.gnu.org/licenses/>.

class Cgroup(object):
    """ Cgroup object to reflect the on-disk structure.

    children: list of children cgroups of this cgroup.
    path: path related to on-disk position, starts at /
    procs: list of processes that are on this cgroup

    addproc: utility method to append a proc to procs
    removeproc: utility method to remove a proc from procs
    """
    
    children = []
    path = ''
    procs = []

    def __init__(self, parent, cgroupmount = None):
        if parent == self:
            raise Exception("Cgroup can't be child of itself")

        if parent is not None:
            parent.children.append(self)
        else:
            self.path = '/'
            self.fspath = cgroupmount
    
    def addproc(self, pid):
        if pid in self.procs:
            raise Exception("pid already on this cgroup")
        else:
            self.procs.append(pid)

    def removeproc(self,pid):
        if pid not in self.prcs:
            raise Exception("pid not on this cgroup")
        else:
            self.procs.remove(pid)
