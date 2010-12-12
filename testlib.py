#!/usr/env python
# -*- coding: utf-8 -*-

import random
from libcgrouptool.skel import Cgroup

root = Cgroup('root', None, cgroupmount = '/sys/fs/cgroup')
child1 = Cgroup('child1', root)
child2 = Cgroup('child2', root)
child3 = Cgroup('child3', child2)
child4 = Cgroup('child4', child3)

objects = [root, child1, child2, child3, child4]

# task tests

tasks = root.tasks
sample = random.sample(tasks, 8)

for item in objects:
    if item.name != 'root':
        pid1 = sample.pop()
        pid2 = sample.pop()
        item.addtask(pid1)
        item.addtask(pid2)
    print 'name', item.name
    if item.parent is not None:
        print 'parent', item.parent.name
    else:
        print 'parent'
    print 'children', [i.name for i in item.children]
    print 'siblings', [i.name for i in item.siblings]
    print 'path', item.path
    print 'fspath', item.fspath
    print 'tasks', item.tasks
    print '-------'


# Finish it
root.remove_group()
