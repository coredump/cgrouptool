#!/usr/env python
# -*- coding: utf-8 -*-

from libcgrouptool.skel import Cgroup

root = Cgroup('root', None, cgroupmount = '/sys/fs/cgroup')
child1 = Cgroup('child1', root)
child2 = Cgroup('child2', root)
child3 = Cgroup('child3', child2)
child4 = Cgroup('child4', child3)

objects = [root, child1, child2, child3, child4]

for item in objects:
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

root.remove_group()
