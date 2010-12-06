libcgrouptools
==============

.. module:: libcgrouptool

Provides cgrouptool and cgrouptoold with all it needs. Provides tools
and data to manipulate cgroups and reflect the changes on disk.

.. module:: libcgrouptool.skel
    
Basic classes and functions.

.. class:: Cgroup(parent, cgroupmount = None)

    .. attribute:: children

       list of children cgroups of this cgroup.
    .. attribute:: path
    
       path related to on-disk position, starts at /
    .. attribute:: procs
       
       list of processes that are on this cgroup
    .. method:: addproc(self, pid) 
       
       utility method to append a proc to procs
    .. method:: removeproc(self,pid)
       
       utility method to remove a proc from procs
