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

class CgroupError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Cgroup:
    """ Cgroup object to reflect the on-disk structure.

    children: list of children cgroups of this cgroup.
    path: path related to on-disk position, starts at /
    procs: list of processes that are on this cgroup

    addproc: utility method to append a proc to procs
    removeproc: utility method to remove a proc from procs
    """
    
    def __init__(self, name, parent_class, cgroupmount = None):
        if parent_class == self:
            raise CgroupError("Cgroup can't be child of itself")

        if parent_class is not None:
            self.parent = parent_class
            self.parent.children.append(self)
            self.siblings = self.parent.children
            self.__create_group(name)   
        else:
            self.parent = None
            self.path = '/'
            self.fspath = cgroupmount

        self.children = []
        self.siblings = []
        self.procs = []
        self.name = name
    
    def __create_group(self, name):
        new_path = os.path.join(self.parent.fspath, name)
        if os.path.exists(new_path):
            raise CgroupError("Group already exists")
        else:
            try:
                os.mkdir(new_path)
            except:
                raise CgroupError("Can't create the cgroup directory")
        self.fspath = new_path
        self.path = self.parent.path.rstrip('/') + '/%s' % name
        
    def __remove_group(self, name):
        if len(self.children) > 0:
            raise CgroupError("Can't remove a group with children")
        try:
            os.rmdir(self.fspath)
        except:
            raise CgroupError("Can't remove the cgroup directory")
        self.parent.children.remove(self) 

    def __add_pid_to_cgroup(self, pid):
        tsk_file_path = os.path.join(self.fspath, 'tasks')
        tsk_file = open(tsk_file_path)
        try:
            tsk_file.write(str(pid))
        except:
            raise CgroupError("Can't write to cgroup's tasks file")

    def __remove_pid_from_cgroup(pid):
        """In truth, moves the pid to the cgroup's parent cgroup,
           there's no way to remove it from the tasks file"""
        tsk_file_path = os.path.join(self.parent.fspath, 'tasks')
        tsk_file = open(tsk_file_path)
        try:
            tsk_file.write(str(pid))
        except:
            raise CgroupError("Cant't write to parent cgroup's tasks file") 
    
    def addproc(self, pid):
        if pid in self.procs:
            raise CgroupError("pid already on this cgroup")
        else:
            self.procs.append(pid)
            self.__add_pid_to_cgroup(pid)

    def removeproc(self,pid):
        if pid not in self.prcs:
            raise CgroupError("pid not on this cgroup")
        else:
            self.procs.remove(pid)
            self.__remove_pid_from_cgroup(pid)
