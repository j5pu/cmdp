#!/usr/bin/env spython
# coding=utf-8

"""
Change EUID at startup
"""
import errno
import os
import stat
import sys
import builtins


def setuid():
    """Sets euid to uid if script is run with SUDO or special execution user bit is set.

    With sudo, our scripts will work but other scripts and modules that require sudo will not work.
    :return:
    """
    uid = os.getuid()
    if not hasattr(builtins, "uid") and (
            (os.stat(os.path.realpath(sys.executable)).st_mode & stat.S_ISUID == stat.S_ISUID) or (
            uid := os.environ.get("SUDO_UID", 0))):
        builtins.uid = os.getuid()
        builtins.euid = os.geteuid()
        os.seteuid(uid)


def elevate():
    """Other https://github.com/netinvent/command_runner/blob/master/command_runner/elevate.py.

    :return:
    """
    if os.getuid() == 0:
        return

    commands = ["sudo", sys.executable, *sys.argv]

    for args in commands:
        try:
            os.execl(args[0], *args)
        except OSError as e:
            if e.errno != errno.ENOENT or args[0] == "sudo":
                raise


print(sys.argv)
def output():
    print(f"{os.getuid()=}")
    print(f"{os.geteuid()=}")
    if hasattr(builtins, "uid"):
        print(f"{builtins.uid=}")
        print(f"{builtins.euid=}")


output()
setuid()
output()
