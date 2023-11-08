"""Errors Module."""
__all__ = (
    "CalledProcessError",
    "CmdError",
    "CommandNotFoundError",
    "InvalidArgumentError",
)

import signal
import subprocess
from collections.abc import Sequence
from typing import AnyStr

from nodeps.modules.typings import StrOrBytesPath


class _NoDepsBaseError(Exception):
    """Base Exception from which all other custom Exceptions defined in semantic_release inherit."""


class CalledProcessError(subprocess.SubprocessError):
    """Patched :class:`subprocess.CalledProcessError`.

    Raised when run() and the process returns a non-zero exit status.

    Attributes:
        cmd: The command that was run.
        returncode: The exit code of the process.
        output: The output of the process.
        stderr: The error output of the process.
        completed: :class:`subprocess.CompletedProcess` object.
    """

    returncode: int
    cmd: StrOrBytesPath | Sequence[StrOrBytesPath]
    output: AnyStr | None
    stderr: AnyStr | None
    completed: subprocess.CompletedProcess | None

    # noinspection PyShadowingNames
    def __init__(
            self,
            returncode: int | None = None,
            cmd: StrOrBytesPath | Sequence[StrOrBytesPath] | None = None,
            output: AnyStr | None = None,
            stderr: AnyStr | None = None,
            completed: subprocess.CompletedProcess | None = None,
    ) -> None:
        r"""Patched :class:`subprocess.CalledProcessError`.

        Args:
            cmd: The command that was run.
            returncode: The exit code of the process.
            output: The output of the process.
            stderr: The error output of the process.
            completed: :class:`subprocess.CompletedProcess` object.

        Examples:
            >>> import subprocess
            >>> 3/0  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ZeroDivisionError: division by zero
            >>> subprocess.run(["ls", "foo"], capture_output=True, check=True)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            errors.CalledProcessError:
              Return Code:
                1
            <BLANKLINE>
              Command:
                ['ls', 'foo']
            <BLANKLINE>
              Stderr:
                b'ls: foo: No such file or directory\n'
            <BLANKLINE>
              Stdout:
                b''
            <BLANKLINE>
        """
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr
        self.completed = completed
        if self.returncode is None:
            self.returncode = self.completed.returncode
            self.cmd = self.completed.args
            self.output = self.completed.stdout
            self.stderr = self.completed.stderr

    def _message(self):
        if self.returncode and self.returncode < 0:
            try:
                return f"Died with {signal.Signals(-self.returncode)!r}."
            except ValueError:
                return f"Died with with unknown signal {-self.returncode}."
        else:
            return f"{self.returncode:d}"

    def __str__(self):
        """Returns str."""
        return f"""
  Return Code:
    {self._message()}

  Command:
    {self.cmd}

  Stderr:
    {self.stderr}

  Stdout:
    {self.output}
"""

    @property
    def stdout(self) -> str:
        """Alias for output attribute, to match stderr."""
        return self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


class CmdError(subprocess.CalledProcessError):
    """Raised when run() and the process returns a non-zero exit status.

    Attribute:
      process: The CompletedProcess object returned by run().
    """

    def __init__(self, process: subprocess.CompletedProcess | None = None) -> None:
        """Init."""
        super().__init__(process.returncode, process.args, output=process.stdout, stderr=process.stderr)

    def __str__(self) -> str:
        """Str."""
        value = super().__str__()
        if self.stderr is not None:
            value += "\n" + self.stderr
        if self.stdout is not None:
            value += "\n" + self.stdout
        return value


class CommandNotFoundError(_NoDepsBaseError):
    """Raised when command is not found."""


class InvalidArgumentError(_NoDepsBaseError):
    """Raised when function is called with invalid argument."""


subprocess.CalledProcessError = CalledProcessError
