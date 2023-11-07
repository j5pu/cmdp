"""Typings Module."""
__all__ = (
    "AnyIO",
    "ChainLiteral",
    "ExcType",
    "GitSchemeLiteral",
    "ModuleSpec",
    "OpenIO",
    "StrOrBytesPath",
    "ThreadLock",
    "RunningLoop",
    "LockClass",
)

import asyncio
import importlib
import os
import threading
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from typing import IO, AnyStr, BinaryIO, Literal, TypeAlias

AnyIO = IO[AnyStr]
ChainLiteral: TypeAlias = Literal["all", "first", "unique"]
ExcType: TypeAlias = type[Exception] | tuple[type[Exception], ...]
GitSchemeLiteral = Literal["git+file", "git+https", "git+ssh", "https", "ssh"]
ModuleSpec = importlib._bootstrap.ModuleSpec
OpenIO = BinaryIO | BufferedRandom | BufferedReader | BufferedWriter | FileIO | IO | TextIOWrapper
StrOrBytesPath = AnyStr | os.PathLike[str] | os.PathLike[bytes]
ThreadLock = threading.Lock
RunningLoop = asyncio.events._RunningLoop
LockClass = type(ThreadLock())
