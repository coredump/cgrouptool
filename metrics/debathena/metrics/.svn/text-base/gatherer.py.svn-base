#!/usr/bin/python
"""Debathena metrics collection.
Usage: debathena-metrics

This script runs during a login session, collecting statistics on what
programs are run by the user over the course of the session.

This script also collects notifications about software being installed
through apt.

At the end of the login session, the collected information is batched
and sent to the Athena syslog server, along with the duration of the
login session.
"""


import errno
import fcntl
import os
import pwd
import socket
import syslog
import time
import uuid
import re
import os.path

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject

from debathena.metrics import connector


DBUS_OBJECT = '/'
DBUS_INTERFACE = 'edu.mit.debathena.Metrics'


LOG_LEVEL = syslog.LOG_LOCAL0 | syslog.LOG_INFO
LOG_SERVER = ('wslogger.mit.edu', 514)

SCHROOT_PAT = re.compile('/var/lib/schroot/mount/login-[^/]+')

DIRECTORY_BLACKLIST = set([
    '/bin',
    '/sbin',
    '/usr/lib/schroot',
    '/usr/lib/cups/backend',
    '/usr/lib/cups/backend-available',
    ])

PROGRAM_BLACKLIST = set([
    '/lib/udev/vol_id',
    '/usr/bin/aklog',
    '/usr/bin/amixer',
    '/usr/bin/apt-config',
    '/usr/bin/athdir',
    '/usr/bin/authwatch',
    '/usr/bin/basename',
    '/usr/bin/bluetooth-applet',
    '/usr/bin/canberra-gtk-play',
    '/usr/bin/compiz.real',
    '/usr/bin/cpp-4.3',
    '/usr/bin/cut',
    '/usr/bin/dbus-launch',
    '/usr/bin/dbus-send',
    '/usr/bin/desync',
    '/usr/bin/dirname',
    '/usr/bin/dpkg-query',
    '/usr/bin/expr',
    '/usr/bin/flock',
    '/usr/bin/fs',
    '/usr/bin/gawk',
    '/usr/bin/gconftool-2',
    '/usr/bin/gdmflexiserver',
    '/usr/bin/get_message',
    '/usr/bin/getent',
    '/usr/bin/glxinfo',
    '/usr/bin/gtk-window-decorator',
    '/usr/bin/gnome-keyring-daemon',
    '/usr/bin/gnome-panel',
    '/usr/bin/gnome-power-manager',
    '/usr/bin/gnome-session',
    '/usr/bin/gnome-session-save',
    '/usr/bin/gnome-screensaver',
    '/usr/bin/gnome-terminal',
    '/usr/bin/gpasswd',
    '/usr/bin/gpg',
    '/usr/bin/gpgconf',
    '/usr/bin/hesinfo',
    '/usr/bin/id',
    '/usr/bin/ionice',
    '/usr/bin/klist',
    '/usr/bin/krb524init',
    '/usr/bin/lert',
    '/usr/bin/lspci',
    '/usr/bin/metacity',
    '/usr/bin/nautilus',
    '/usr/bin/net.samba3',
    '/usr/bin/nm-applet',
    '/usr/bin/pactl',
    '/usr/bin/perl',
    '/usr/bin/pgrep',
    '/usr/bin/pulseaudio',
    '/usr/bin/python2.6',
    '/usr/bin/quota.debathena',
    '/usr/bin/renice',
    '/usr/bin/schroot',
    '/usr/bin/scim',
    '/usr/bin/scim-bridge',
    '/usr/bin/seahorse-agent',
    '/usr/bin/setfacl',
    '/usr/bin/ssh-agent',
    '/usr/bin/stat',
    '/usr/bin/sudo',
    '/usr/bin/tac',
    '/usr/bin/tail',
    '/usr/bin/tokens',
    '/usr/bin/tput',
    '/usr/bin/xargs',
    '/usr/bin/xdg-user-dirs-gtk-update',
    '/usr/bin/xdg-user-dirs-update',
    '/usr/bin/xdpyinfo',
    '/usr/bin/xhost',
    '/usr/bin/xkbcomp',
    '/usr/bin/xrdb',
    '/usr/bin/xset',
    '/usr/bin/xsetroot',
    '/usr/bin/xvinfo',
    '/usr/lib/ConsoleKit/ck-collect-session-info',
    '/usr/lib/ConsoleKit/ck-get-x11-server-pid',
    '/usr/lib/bonobo-activation/bonobo-activation-server',
    '/usr/lib/cups/daemon/cups-polld',
    '/usr/lib/evolution/2.26/evolution-alarm-notify',
    '/usr/lib/evolution/evolution-data-server-2.26',
    '/usr/lib/fast-user-switch-applet/fast-user-switch-applet',
    '/usr/lib/gcc/i486-linux-gnu/4.3/cc1',
    '/usr/lib/gnome-applets/mixer_applet2',
    '/usr/lib/gnome-applets/stickynotes_applet',
    '/usr/lib/gnome-applets/trashapplet',
    '/usr/lib/gnome-session/helpers/gnome-settings-daemon-helper',
    '/usr/lib/gnome-settings-daemon/gnome-settings-daemon',
    '/usr/lib/gvfs/gvfs-fuse-daemon',
    '/usr/lib/gvfs/gvfs-gphoto2-volume-monitor',
    '/usr/lib/gvfs/gvfs-hal-volume-monitor',
    '/usr/lib/gvfs/gvfsd',
    '/usr/lib/gvfs/gvfsd-burn',
    '/usr/lib/gvfs/gvfsd-trash',
    '/usr/lib/hal/hal-acl-tool',
    '/usr/lib/indicator-applet/indicator-applet',
    '/usr/lib/libgconf2-4/gconf-sanity-check-2',
    '/usr/lib/libgconf2-4/gconfd-2.debathena-orig',
    '/usr/lib/libvte9/gnome-pty-helper',
    '/usr/lib/notify-osd/notify-osd',
    '/usr/lib/policykit/polkit-read-auth-helper',
    '/usr/lib/pulseaudio/pulse/gconf-helper',
    '/usr/sbin/chroot',
    '/usr/sbin/cupsd',
    ])

def make_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


class Metrics(dbus.service.Object):
    def __init__(self, loop, uid, *args):
        super(Metrics, self).__init__(*args)

        self.loop = loop
        self.uid = uid
        self.installed_packages = set()
        self.executed_programs = set()
        self.start_time = time.time()
        self.session_uuid = str(uuid.uuid4())

        self.proc_conn = connector.Connector()
        make_non_blocking(self.proc_conn)
        self.setup_io_watch()

        dbus.SystemBus().add_signal_receiver(
            self.install_package,
            signal_name='InstallPackage',
            dbus_interface=DBUS_INTERFACE,
            path=DBUS_OBJECT,
            )

        dbus.SystemBus().add_signal_receiver(
            self.logout,
            signal_name='LogOut',
            dbus_interface=DBUS_INTERFACE,
            path=DBUS_OBJECT,
            )

    def setup_io_watch(self):
        gobject.io_add_watch(
            self.proc_conn,
            gobject.IO_IN,
            self.setup_run_program,
            )

    def setup_run_program(self, fd, cond):
        gobject.timeout_add(
            1,
            self.run_program,
            fd,
            cond,
            )
        return False

    def run_program(self, fd, cond):
        try:
            while True:
                try:
                    ev = fd.recv_event()
                except IOError, e:
                    if e.errno == errno.EAGAIN:
                        break

                if ev.what == connector.PROC_EVENT_EXEC:
                    try:
                        prog = os.readlink("/proc/%d/exe" % ev.process_pid)
                        # reactivate-1.x
                        if prog.startswith('/login'):
                            prog = prog[len('/login'):]
                        # reactivate-2.x
                        elif prog.startswith('/var/lib/schroot/mount'):
                            prog = SCHROOT_PAT.sub('', prog)
                        if (prog not in PROGRAM_BLACKLIST) and (os.path.dirname(prog) not in DIRECTORY_BLACKLIST):
                            self.executed_programs.add(prog)
                    except OSError, e:
                        if e.errno == errno.ENOENT:
                            continue
        except Exception, e:
            try:
                syslog.openlog("debathena-metrics", syslog.LOG_NOWAIT | syslog.LOG_NDELAY, syslog.LOG_LOCAL0)
                syslog.syslog(syslog.LOG_ERR, str(e))
                syslog.closelog()
            except:
                pass

        self.setup_io_watch()
        return False

    def install_package(self, package):
        self.installed_packages.add(str(package))

    def logout(self):
        session_length = time.time() - self.start_time

        lines = []
        lines.append('session_len: %d' % session_length)

        for p in self.installed_packages:
            lines.append('installed_package: %s' % p)

        for p in self.executed_programs:
            lines.append('executed_programs: %s' % p)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for l in lines:
            s.sendto('<%d>debathena-metrics %s: %s\n' % (LOG_LEVEL, self.session_uuid, l),
                     LOG_SERVER)

        self.loop.quit()


def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    uid = pwd.getpwnam(os.environ['USER']).pw_uid

    loop = gobject.MainLoop()
    m = Metrics(loop, uid)
    loop.run()


if __name__ == '__main__':
    main()
