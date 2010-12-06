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

import os

class Cgroup(object):
    """ Cgroup object to reflect the on-disk structure.

    children: list of children cgroups of this cgroup.
    path: path related to on-disk position, starts at /
    procs: list of processes that are on this cgroup

    addproc: utility method to append a proc to procs
    removeproc: utility method to remove a proc from procs
    """
    
    children = []
    siblings = None
    path = ''
    fspath = ''
    procs = []

    def __init__(self, name, parent, cgroupmount = None):
        if parent == self:
            raise Exception("Cgroup can't be child of itself")
            return

        if parent is not None:
            parent.children.append(self)
            self.parent = parent
            self.siblings = self.parent.children
            self.__create_group(name)   
        else:
            self.path = '/'
            self.fspath = cgroupmount
    
    def __create_group(self, name):
        new_path = os.path.join(self.parent.fspath, name)
        try:
            os.mkdir(new_path)
        except:
            raise Exception("Can't create the cgroup directory")
            return
        self.fspath = path
        self.path = self.parent.path.rstrip('/') + '/%s' % name
        
    def __remove_group(self, name):
        if len(self.children) > 0:
            raise Exception("Can't remove a group with children")
            return
        try:
            os.rmdir(self.fspath)
        except:
            raise Exception("Can't remove the cgroup directory")
            return
        self.parent.children.remove(self) 

    def __add_pid_to_cgroup(self, pid):
        tsk_file_path = os.path.join(self.fspath, 'tasks')
        tsk_file = open(tsk_file_path)
        try:
            tsk_file.write(str(pid))
        except:
            raise Exception("Can't write to cgroup's tasks file")

    def __remove_pid_from_cgroup(pid):
        """In truth, moves the pid to the cgroup's parent cgroup,
           there's no way to remove it from the tasks file"""
        tsk_file_path = os.path.join(self.parent.fspath, 'tasks')
        tsk_file = open(tsk_file_path)
        try:
            tsk_file.write(str(pid))
        except:
            raise Exception("Cant't write to parent cgroup's tasks file") 
    
    def addproc(self, pid):
        if pid in self.procs:
            raise Exception("pid already on this cgroup")
        else:
            self.procs.append(pid)
            self.__add_pid_to_cgroup(pid)

    def removeproc(self,pid):
        if pid not in self.prcs:
            raise Exception("pid not on this cgroup")
        else:
            self.procs.remove(pid)
            self.__remove_pid_from_cgroup(pid)
