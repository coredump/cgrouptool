#!/usr/env python
# -*- coding: utf-8 -*-

import os
from libcgrouptool.skel import Cgroup

root = Cgroup('root', None, cgroupmount = '/sys/fs/cgroup')
child1 = Cgroup('child1', root)
child2 = Cgroup('child2', root)

objects = [root, child1, child2]

for item in objects:
    print 'name', item.name
    if item.parent is not None:
        print 'parent', item.parent.name
    else:
        print 'parent'
    print 'children', item.children
    print 'siblings', item.siblings
    print 'path', item.path
    print 'fspath', item.fspath
    print '-------'
