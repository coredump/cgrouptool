cgrouptool
===========

Tool to manage and provide some automatic creation and organization of cgroups
available on the Linux kernel 2.6

* ligcgrouptool is the barebones of all operation
* cgrouptoold will be a daemon to provide automatic cgroup manipulation based
  on a config file
* cgrouptool will be a command line tool to talk to the daemon and check stuff

Requisites
==========

- A kernel compiled with:

1. Cgroups support (CONFIG_CGROUPS=y)
2. Netlink proc events support (CONFIG_CONNECTOR=y and CONFIG_PROC_EVENTS=y)
3. Python >= 2.5
