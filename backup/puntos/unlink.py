#!/usr/bin/env python
# coding=utf-8
"""
Uninstall script.
Shamelessly copied from:
https://github.com/anishathalye/dotbot/issues/152#issuecomment-394129600
"""
import shutil
from pathlib import Path

from puntos._vendor.dotbot.cli import read_config
from puntos._vendor.dotbot.messenger.messenger import Messenger
from puntos._vendor.dotbot.config import ReadingError
from puntos._vendor.dotbot.dispatcher import DispatchError

log = Messenger()

CONFIG = Path("/Users/j5pu/.dotfiles/install.conf.yaml")
DOTFILES = CONFIG.parent


def unlink(dest):
    dest = Path(dest)
    if not dest.is_absolute():
        dest = dest.expanduser()
    src = dest.resolve().absolute()
    if dest.is_symlink() and src.is_relative_to(DOTFILES):
        try:
            if not DRY:
                dest.unlink(True)
                if src.is_file():
                    shutil.copyfile(src, dest)
                    shutil.copystat(src, dest)
                elif src.is_dir():
                    shutil.copytree(src, dest, symlinks=True)
                    shutil.copystat(src, dest)
            log.info(f'{src} => {dest}')
        except shutil.Error as exc:
            log.warning(exc)
    elif dest.is_dir():
        scan_home(dest)


def scan_config():
    try:
        for section in read_config(CONFIG):
            if 'link' in section:
                for target in section['link']:
                    unlink(target)

    except (ReadingError, DispatchError) as e:
        log.error("%s" % e)
        exit(1)
    except KeyboardInterrupt:
        log.error("\n==> Operation aborted")
        exit(1)


def scan_home(start=None):
    for dest in Path(start or "~").expanduser().iterdir():
        unlink(dest)


# HACER: Check que son identical with filecmp.cmp and filecmp.dircmp

try:
    DRY = True
    scan_config()
    scan_home()
except OSError as exception:
    if "File name too long" not in repr(exception):
        raise exception
    log.warning(exception)

