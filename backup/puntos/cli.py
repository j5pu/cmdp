# coding=utf-8
"""
Puntos Cli Module
"""
import shutil
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pathlib import Path

import typer

from _vendor import dotbot
from _vendor.dotbot.messenger import Messenger
from _vendor.dotbot.config import ReadingError
from _vendor.dotbot.dispatcher import DispatchError

from .functions import version
from .constants import DOTFILES_CONFIG
from .variables import PUNTOS_SOURCES

__all__ = (
    "app",
)

app = typer.Typer(add_completion=False, context_settings=dict(help_option_names=['-h', '--help']),
                  name=PUNTOS_SOURCES.name)

tasks: list[dict] = dotbot.cli.read_config(DOTFILES_CONFIG)
parser: ArgumentParser = ArgumentParser(formatter_class=RawTextHelpFormatter)
log = Messenger()


def _unlink(keep: bool = False, dry_run: bool = False):
    try:
        for section in tasks:
            if 'link' in section:
                log.info(section)
                for target in section['link']:
                    target = Path(target)
                    if not target.is_absolute():
                        target = target.expanduser()
                    if target.is_symlink():
                        source = target.resolve().absolute()
                        prefix = ""
                        if not dry_run:
                            if keep:
                                target.unlink(missing_ok=True)
                                if source.is_file():
                                    shutil.copyfile(source, target)
                                    shutil.copystat(source, target)
                                elif source.is_dir():
                                    shutil.copytree(source, target, symlinks=True)
                                    shutil.copystat(source, target)
                            else:
                                prefix = '✘ '
                                source.replace(target)
                        log.info(f'{prefix}{source} -> {target}')
    except (ReadingError, DispatchError) as e:
        log.error("%s" % e)
        exit(1)
    except KeyboardInterrupt:
        log.error("\n==> Operation aborted")
        exit(1)


@app.command()
def add(path: list[Path]):
    """"Adds paths to config file"""
    print(path)


def config():
    """
    Shows valid configuration variable names and values.
    Precedence: Environment Variable -> settings.ini -> .env in cwd.

    Defaults defined in: :mod:`puntos.customize`
    """


@app.command()
def install(exit_on_failure: bool = False, quiet: bool = False,
            super_quiet: bool = False, verbose: bool = False):
    """Install symlinks from dotfiles repository to original location"""
    pass


@app.command()
def copy(dry_run: bool = False):
    """Copy dotfiles to its original location and keep a copy in dotfiles respository"""
    _unlink(keep=True, dry_run=dry_run)


@app.command()
def replace(dry_run: bool = False):
    """Replaces dotfiles at destination and remove the copy in dotfiles repository"""
    _unlink(dry_run=dry_run)


@app.command()
def version():
    """Shows version and exit"""
    print(version())


if __name__ == '__main__':
    try:
        from typer import Exit

        Exit(app())
    except KeyboardInterrupt:
        print('Aborted!')
        Exit(1)
