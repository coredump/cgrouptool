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

    The cgroup hierarchy must start with a instance of this class called 'root'
    with 'parent_class' equal to None and cgroupmount pointing to the cgroup
    filesystem mountpoint (normally /sys/fs/cgroup/). From there the other
    instances will use the root object as parent_class.

    children: list of children cgroups of this cgroup.
    path: path related to on-disk position, starts at /
    tasks: list of processes that are on this cgroup
    siblings: child groups at the same level

    addtask: utility method to append a task to tasks
    removetask: utility method to remove a task from tasks
    remove_group: remove a cgroup from disk, recursively remove children, also
                  remove any tasks attached to the cgroups.
    """

    def __init__(self, name, parent_class, cgroupmount = None):
        if parent_class == self:
            raise CgroupError("Cgroup can't be child of itself")

        if parent_class is not None:
            self.parent = parent_class
            self.parent.children.append(self)
            self.siblings = self.parent.children
            self.__create_group(name)
            self.tasks = []
            self.name = name
        else:
            self.parent = None
            self.name = 'root'
            self.path = '/'
            self.fspath = cgroupmount
            self.tasks = []

        self.children = []
        self.siblings = []
        self.__update_tasks()

    def __update_tasks(self):
        # Tasks must reflect the tasks file on disk
        # TODO: This may be a little read intensive during multiple group 
        #       creation or multiple task insertion. Must test.
        self.tasks = []
        try:
            task_file_path = os.path.join(self.fspath, "tasks")
            for line in open(task_file_path):
                self.tasks.append(line.strip())
        except Exception, err:
            raise CgroupError("Problems updating tasks: %s" % err)

        if self.name != 'root':
            self.parent.__update_tasks()

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

    def __add_task_to_cgroup(self, task):
        task_file_path = os.path.join(self.fspath, "tasks")
        try:
            task_file = open(task_file_path, "w")
            task_file.write(str(task))
            task_file.close()
        except Exception as err:
            raise CgroupError("Can't write to cgroup's tasks file: %s" % err)
        self.__update_tasks()

    def __remove_task_from_cgroup(self, task):
        """In truth, moves the task to the cgroup's parent cgroup,
           there's no way to remove it from the tasks file"""
        # Barrier to prevent removing tasks from root cgroup
        if self.name == 'root':
            raise "Can't remove tasks from root cgroup"
        try:
            self.parent.addtask(task)
        except Exception as err:
            raise CgroupError("Can't add task to parent cgroup %s" % err)

    def remove_group(self, name = None):
        if name == None:
            name = self.name
        # Copies the list of objects or the recursive removal will mess up the
        # for loop
        to_remove = self.children[:]
        if len(to_remove) > 0:
            for child in to_remove:
                child.remove_group(child.name)
        if self.name != 'root':
            if len(self.tasks) > 0:
                for task in self.tasks:
                    self.__remove_task_from_cgroup(task)
            try:
                os.rmdir(self.fspath)
            except:
                raise CgroupError("Can't remove the cgroup directory")
            self.parent.children.remove(self)

    def addtask(self, task):
        if task in self.tasks:
            raise CgroupError("task already on this cgroup")
        else:
            self.__add_task_to_cgroup(task)

    def removetask(self,task):
        if task not in self.tasks:
            raise CgroupError("task not on this cgroup")
        else:
            self.__remove_task_from_cgroup(task)

