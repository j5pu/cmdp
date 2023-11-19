"""Classes Module."""
from __future__ import annotations

__all__ = (
    "Chain",
    "ColorLogger",
    "ConfigParser",
    "dd",
    "dictsort",
    "getter",
    "LetterCounter",
    "NamedtupleMeta",
    "Noset",
    "NOSET",
)

import abc
import collections
import configparser
import logging
import string
import types
from collections.abc import Callable, Iterable, MutableMapping
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar, Union

from nodeps.modules.functions import toiter

if TYPE_CHECKING:
    from collections.abc import Hashable

    from nodeps.modules.typings import ChainLiteral

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class Chain(collections.ChainMap):
    # noinspection PyUnresolvedReferences
    """Variant of chain that allows direct updates to inner scopes and returns more than one value, not the first one.

    Examples:
        >>> from nodeps import Chain
        >>>
        >>> class Test3:
        ...     a = 2
        >>>
        >>> class Test4:
        ...     a = 2
        >>>
        >>> Test1 = collections.namedtuple('Test1', 'a b')
        >>> Test2 = collections.namedtuple('Test2', 'a d')
        >>> test1 = Test1(1, 2)
        >>> test2 = Test2(3, 5)
        >>> test3 = Test3()
        >>> test4 = Test4()
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2))]
        >>> chain = Chain(*maps)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 2}]
        >>> chain = Chain(*maps, rv="first")
        >>> assert chain['a'] == 1
        >>> chain = Chain(*maps, rv="all")
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 1}, {'z': 2}]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)),\
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 2}]
        >>> chain = Chain(*maps, rv="first")
        >>> assert chain['a'] == 1
        >>> chain = Chain(*maps, rv="all")
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 1}, {'z': 2}, 1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> del chain['a']
        >>> assert chain == Chain({'b': 2}, {'c': 3}, {'d': 4}, test1, test2)
        >>> assert chain['a'] == [1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> assert chain.delete('a') == Chain({'b': 2}, {'c': 3}, {'d': 4}, test1, test2)
        >>> assert chain.delete('a')['a'] == [1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps, rv="first")
        >>> del chain['a']
        >>> del maps[0]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>>
        >>> assert chain['a'] == 2
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps, rv="first")
        >>> new = chain.delete('a')
        >>> del maps[0]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>> assert new.delete('a')
        >>> del maps[1]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>>
        >>> assert new['a'] == 3
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test3]
        >>> chain = Chain(*maps)
        >>> del chain['a']
        >>> assert chain[4] == []
        >>> assert not hasattr(test3, 'a')
        >>> assert chain.set('a', 9)
        >>> assert chain['a'] == [9, 1]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test4]
        >>> chain = Chain(*maps)
        >>> chain.set('j', 9)  # doctest: +ELLIPSIS
        Chain({'a': 1, 'b': 2, 'j': 9}, {'a': 2, 'c': 3}, {'a': 3, 'd': 4}, {'a': {'z': 1}}, {'a': {'z': 1}}, \
{'a': {'z': 2}}, Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> assert [maps[0]['j']] == chain['j'] == [9]
        >>> chain.set('a', 10)  # doctest: +ELLIPSIS
        Chain({'a': 10, 'b': 2, 'j': 9}, {'a': 10, 'c': 3}, {'a': 10, 'd': 4}, {'a': 10}, {'a': 10}, {'a': 10}, \
Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> # noinspection PyUnresolvedReferences
        >>> assert [maps[0]['a'], 1] == chain['a'] == [maps[7].a, 1] == [10, 1]  # 1 from namedtuple
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test4]
        >>> chain = Chain(*maps, rv="first")
        >>> chain.set('a', 9)  # doctest: +ELLIPSIS
        Chain({'a': 9, 'b': 2}, {'a': 2, 'c': 3}, {'a': 3, 'd': 4}, {'a': {'z': 1}}, {'a': {'z': 1}}, \
{'a': {'z': 2}}, Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> assert maps[0]['a'] == chain['a'] == 9
        >>> assert maps[1]['a'] == 2
    """

    rv: ChainLiteral = "unique"
    default: Any = None
    maps: list[Iterable | NamedtupleMeta | MutableMapping] = []  # noqa: RUF012

    def __init__(self, *maps, rv: ChainLiteral = "unique", default: Any = None) -> None:
        """Init."""
        super().__init__(*maps)
        self.rv = rv
        self.default = default

    def __getitem__(self, key: Hashable) -> Any:  # noqa: PLR0912
        """Get item."""
        rv = []
        for mapping in self.maps:
            if hasattr(mapping, "_field_defaults"):
                mapping = mapping._asdict()  # noqa: PLW2901
            elif hasattr(mapping, "asdict"):
                to_dict = mapping.__class__.asdict
                if isinstance(to_dict, property):
                    mapping = mapping.asdict  # noqa: PLW2901
                elif callable(to_dict):
                    mapping = mapping.asdict()  # noqa: PLW2901
            if hasattr(mapping, "__getitem__"):
                try:
                    value = mapping[key]
                    if self.rv == "first":
                        return value
                    if (self.rv == "unique" and value not in rv) or self.rv == "all":
                        rv.append(value)
                except KeyError:
                    pass
            elif (
                    hasattr(mapping, "__getattribute__")
                    and isinstance(key, str)
                    and not isinstance(mapping, (tuple | bool | int | str | bytes))
            ):
                try:
                    value = getattr(mapping, key)
                    if self.rv == "first":
                        return value
                    if (self.rv == "unique" and value not in rv) or self.rv == "all":
                        rv.append(value)
                except AttributeError:
                    pass
        return self.default if self.rv == "first" else rv

    def __delitem__(self, key: Hashable) -> Chain:
        """Delete item."""
        index = 0
        deleted = []
        found = False
        for mapping in self.maps:
            if mapping:
                if not isinstance(mapping, (tuple | bool | int | str | bytes)):
                    if hasattr(mapping, "__delitem__"):
                        if key in mapping:
                            del mapping[key]
                            if self.rv == "first":
                                found = True
                    elif hasattr(mapping, "__delattr__") and hasattr(mapping, key) and isinstance(key, str):
                        delattr(mapping.__class__, key) if key in dir(mapping.__class__) else delattr(mapping, key)
                        if self.rv == "first":
                            found = True
                if not mapping:
                    deleted.append(index)
                if found:
                    break
            index += 1
        for index in reversed(deleted):
            del self.maps[index]
        return self

    def delete(self, key: Hashable) -> Chain:
        """Delete item."""
        del self[key]
        return self

    def __setitem__(self, key: Hashable, value: Any) -> Chain:  # noq: C901
        """Set item."""
        found = False
        for mapping in self.maps:
            if mapping:
                if not isinstance(mapping, (tuple | bool | int | str | bytes)):
                    if hasattr(mapping, "__setitem__"):
                        if key in mapping:
                            mapping[key] = value
                            if self.rv == "first":
                                found = True
                    elif hasattr(mapping, "__setattr__") and hasattr(mapping, key) and isinstance(key, str):
                        setattr(mapping, key, value)
                        if self.rv == "first":
                            found = True
                if found:
                    break
        if not found and not isinstance(self.maps[0], (tuple | bool | int | str | bytes)):
            if hasattr(self.maps[0], "__setitem__"):
                self.maps[0][key] = value
            elif hasattr(self.maps[0], "__setattr__") and isinstance(key, str):
                setattr(self.maps[0], key, value)
        return self

    def set(self, key: Hashable, value: Any) -> Chain:  # noqa: A003
        """Set item."""
        return self.__setitem__(key, value)


class ColorLogger(logging.Formatter):
    """Color logger class."""

    black = "\x1b[30m"
    blue = "\x1b[34m"
    cyan = "\x1b[36m"
    gr = "\x1b[32m"
    grey = "\x1b[38;21m"
    mg = "\x1b[35m"
    red = "\x1b[31;21m"
    red_bold = "\x1b[31;1m"
    reset = "\x1b[0m"
    white = "\x1b[37m"
    yellow = "\x1b[33;21m"
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    vertical = f"{red}|{reset} "
    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: f"{cyan}%(levelname)8s{reset} {vertical}"
                      f"{cyan}%(name)s{reset} {vertical}"
                      f"{cyan}%(filename)s{reset}:{cyan}%(lineno)d{reset} {vertical}"
                      f"{gr}%(extra)s{reset} {vertical}"
                      f"{cyan}%(message)s{reset}",
        logging.WARNING: f"{yellow}%(levelname)8s{reset} {vertical}"
                         f"{yellow}%(name)s{reset} {vertical}"
                         f"{yellow}%(filename)s{reset}:{yellow}%(lineno)d{reset} {vertical}"
                         f"{gr}%(repo)s{reset} {vertical}"
                         f"{yellow}%(message)s{reset}",
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: red_bold + fmt + reset,
    }

    def format(self, record):  # noqa: A003
        """Format log."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        if "extra" not in record.__dict__:
            record.__dict__["extra"] = ""
        return formatter.format(record)

    @classmethod
    def logger(cls, name: str = __name__) -> logging.Logger:
        """Get logger.

        Examples:
            >>> from nodeps import ColorLogger
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> lo = ColorLogger.logger(NODEPS_PROJECT_NAME)
            >>> lo.info("hola", extra=dict(extra="bapy"))
            >>> lo.info("hola")

        Args:
            name: logger name

        Returns:
            logging.Logger
        """
        l = logging.getLogger(name)
        l.propagate = False
        l.setLevel(logging.DEBUG)
        if l.handlers:
            l.handlers[0].setLevel(logging.DEBUG)
            l.handlers[0].setFormatter(cls())
        else:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(cls())
            l.addHandler(handler)
        return l


class ConfigParser(configparser.ConfigParser):
    """Config parser to get list from setup.cfg."""

    def getlist(self, section: str = "options", option: str = "scripts") -> list:
        """Get list."""
        value = None
        if self.has_section(section):
            value = self.get(section, option) if self.has_option(section, option) else None
        return list(filter(None, (x.strip() for x in value.splitlines()))) if value else []

    def setlist(self, section: str = "options", option: str = "scripts", value: list | None = None):
        """Set list."""
        if value:
            newline = "\n"
            value = f"\n{newline.join(value)}"
            if not self.has_section(section):
                self.add_section(section)
            self.set(section=section, option=option, value=value)
        else:
            self.remove_option(section=section, option=option)


# noinspection PyPep8Naming
class dd(collections.defaultdict):  # noqa: N801
    """Default Dict Helper Class.

    Examples:
        >>> from nodeps import dd
        >>>
        >>> d = dd()
        >>> d
        dd(None, {})
        >>> d[1]
        >>> d.get(1)
        >>>
        >>> d = dd({})
        >>> d
        dd(None, {})
        >>> d[1]
        >>> d.get(1)
        >>>
        >>> d = dd({}, a=1)
        >>> d
        dd(None, {'a': 1})
        >>> d[1]
        >>> d.get(1)
        >>>
        >>> d = dd(dict)
        >>> d
        dd(<class 'dict'>, {})
        >>> d.get(1)
        >>> d
        dd(<class 'dict'>, {})
        >>> d[1]
        {}
        >>> d
        dd(<class 'dict'>, {1: {}})
        >>> d = dd(tuple)
        >>> d
        dd(<class 'tuple'>, {})
        >>> d[1]
        ()
        >>> d.get(1)
        ()
        >>>
        >>> d = dd(True)
        >>> d
        dd(True, {})
        >>> d[1]
        True
        >>> d.get(1)
        True
        >>>
        >>> d = dd({1: 1}, a=1)
        >>> d
        dd(None, {1: 1, 'a': 1})
        >>> d[1]
        1
        >>> d.get(1)
        1
        >>>
        >>> d = dd(list, {1: 1}, a=1)
        >>> d
        dd(<class 'list'>, {1: 1, 'a': 1})
        >>> d[2]
        []
        >>> d
        dd(<class 'list'>, {1: 1, 'a': 1, 2: []})
        >>>
        >>> d = dd(True, {1: 1}, a=1)
        >>> d
        dd(True, {1: 1, 'a': 1})
        >>> d.get('c')
        >>> d['c']
        True
    """

    __slots__ = ("__factory__",)

    def __init__(self, factory: Union[Callable, Any] = None, *args: Any, **kwargs: Any):  # noqa: UP007
        """Init."""

        def dd_factory(value):
            return lambda: value() if callable(value) else value

        iterable = isinstance(factory, Iterable)
        self.__factory__ = None if iterable else factory
        super().__init__(dd_factory(self.__factory__), *((*args, factory) if iterable else args), **kwargs)

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}({self.__factory__}, {dict(self)})"

    __class_getitem__ = classmethod(types.GenericAlias)


# noinspection PyPep8Naming
class dictsort(dict, MutableMapping[_KT, _VT]):  # noqa: N801
    """Dict Sort Class.

    Examples:
        >>> from nodeps import dictsort
        >>>
        >>> d = dictsort(b=1, c=2, a=3)
        >>> assert d.sort() == dictsort({'a': 3, 'b': 1, 'c': 2})
    """

    __slots__ = ()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Init."""
        super().__init__(*args, **kwargs)

    def sort(self) -> dictsort[_KT, _VT]:
        """Sort."""
        return self.__class__({item: self[item] for item in sorted(self)})


# noinspection PyPep8Naming
class getter(Callable[[Any], Any | tuple[Any, ...]]):  # noqa: N801
    """Return a callable object that fetches the given attribute(s)/item(s) from its operand.

    Examples:
        >>> from types import SimpleNamespace
        >>> from pickle import dumps, loads
        >>> from copy import deepcopy
        >>> from nodeps import getter
        >>>
        >>> test = SimpleNamespace(a='a', b='b')
        >>> assert getter('a b')(test) == (test.a, test.b)
        >>> assert getter('a c')(test) == (test.a, None)
        >>> dicts = getter('a c d', default={})(test)
        >>> assert dicts == (test.a, {}, {})
        >>> assert id(dicts[1]) != id(dicts[2])
        >>> assert getter('a')(test) == test.a
        >>> assert getter('a b', 'c')(test) == (test.a, test.b, None)
        >>> assert getter(['a', 'b'], 'c')(test) == (test.a, test.b, None)
        >>> assert getter(['a', 'b'])(test) == (test.a, test.b)
        >>>
        >>> test = dict(a='a', b='b')
        >>> assert getter('a b')(test) == (test['a'], test['b'])
        >>> assert getter('a c')(test) == (test['a'], None)
        >>> dicts = getter('a c d', default={})(test)
        >>> assert dicts == (test['a'], {}, {})
        >>> assert id(dicts[1]) != id(dicts[2])
        >>> assert getter('a')(test) == test['a']
        >>> assert getter('a b', 'c')(test) == (test['a'], test['b'], None)
        >>> assert getter(['a', 'b'], 'c')(test) == (test['a'], test['b'], None)
        >>> assert getter(['a', 'b'])(test) == (test['a'], test['b'])
        >>>
        >>> test = SimpleNamespace(a='a', b='b')
        >>> test1 = SimpleNamespace(d='d', test=test)
        >>> assert getter('d test.a test.a.c test.c test.m.j.k')(test1) == (test1.d, test1.test.a, None, None, None)
        >>> assert getter('a c')(test1) == (None, None)
        >>> dicts = getter('a c d test.a', 'test.b', default={})(test1)
        >>> assert dicts == ({}, {}, test1.d, test1.test.a, test1.test.b)
        >>> assert id(dicts[1]) != id(dicts[2])
        >>> assert getter('a')(test1) is None
        >>> assert getter('test.b')(test1) == test1.test.b
        >>> assert getter(['a', 'test.b'], 'c')(test1) == (None, test1.test.b, None)
        >>> assert getter(['a', 'a.b.c'])(test1) == (None, None)
        >>>
        >>> test = dict(a='a', b='b')
        >>> test1_dict = dict(d='d', test=test)
        >>> assert getter('d test.a test.a.c test.c test.m.j.k')(test1_dict) == \
                getter('d test.a test.a.c test.c test.m.j.k')(test1)
        >>> assert getter('d test.a test.a.c test.c test.m.j.k')(test1_dict) == \
                (test1_dict['d'], test1_dict['test']['a'], None, None, None)
        >>> assert getter('a c')(test1_dict) == (None, None)
        >>> dicts = getter('a c d test.a', 'test.b', default={})(test1_dict)
        >>> assert dicts == ({}, {}, test1_dict['d'], test1_dict['test']['a'], test1_dict['test']['b'])
        >>> assert id(dicts[1]) != id(dicts[2])
        >>> assert getter('a')(test1_dict) is None
        >>> assert getter('test.b')(test1_dict) == test1_dict['test']['b']
        >>> assert getter(['a', 'test.b'], 'c')(test1_dict) == (None, test1_dict['test']['b'], None)
        >>> assert getter(['a', 'a.b.c'])(test1_dict) == (None, None)
        >>>
        >>> encode = dumps(test1_dict)
        >>> test1_dict_decode = loads(encode)
        >>> assert id(test1_dict) != id(test1_dict_decode)
        >>> test1_dict_copy = deepcopy(test1_dict)
        >>> assert id(test1_dict) != id(test1_dict_copy)
        >>>
        >>> assert getter('d test.a test.a.c test.c test.m.j.k')(test1_dict_decode) == \
        (test1_dict_decode['d'], test1_dict_decode['test']['a'], None, None, None)
        >>> assert getter('a c')(test1_dict_decode) == (None, None)
        >>> dicts = getter('a c d test.a', 'test.b', default={})(test1_dict_decode)
        >>> assert dicts == ({}, {}, test1_dict_decode['d'], test1_dict['test']['a'], test1_dict_decode['test']['b'])
        >>> assert id(dicts[1]) != id(dicts[2])
        >>> assert getter('a')(test1_dict_decode) is None
        >>> assert getter('test.b')(test1_dict_decode) == test1_dict_decode['test']['b']
        >>> assert getter(['a', 'test.b'], 'c')(test1_dict_decode) == (None, test1_dict_decode['test']['b'], None)
        >>> assert getter(['a', 'a.b.c'])(test1_dict_decode) == (None, None)

        The call returns:
            - getter('name')(r): r.name/r['name'].
            - getter('name', 'date')(r): (r.name, r.date)/(r['name'], r['date']).
            - getter('name.first', 'name.last')(r):(r.name.first, r.name.last)/(r['name.first'], r['name.last']).
    """

    __slots__ = ("_attrs", "_call", "_copy", "_default", "_mm")

    def __init__(self, attr: str | Iterable[str], *attrs: str, default: bool | Any = None):
        """Init."""
        self._copy: bool = "copy" in dir(type(default))
        self._default: bool | Any = default
        _attrs = toiter(attr)
        attr = _attrs[0]
        attrs = (tuple(_attrs[1:]) if len(_attrs) > 1 else ()) + attrs
        if not attrs:
            if not isinstance(attr, str):
                msg = "attribute name must be a string"
                raise TypeError(msg)
            self._attrs = (attr,)
            names = attr.split(".")

            def func(obj):
                mm = isinstance(obj, MutableMapping)
                count = 0
                total = len(names)
                for name in names:
                    count += 1
                    _default = self._default.copy() if self._copy else self._default
                    if mm:
                        try:
                            obj = obj[name]
                            if not isinstance(obj, MutableMapping) and count < total:
                                obj = None
                                break
                        except KeyError:
                            obj = _default
                            break
                    else:
                        obj = getattr(obj, name, _default)
                return obj

            self._call: Callable[[Any], Any | tuple[Any, ...]] = func
        else:
            self._attrs = (attr, *attrs)
            callers = tuple(self.__class__(item, default=self._default) for item in self._attrs)

            def func(obj):
                return tuple(call(obj) for call in callers)

            self._call = func

    def __call__(self, obj: Any) -> Any | tuple[Any, ...]:
        """Call."""
        return self._call(obj)

    def __reduce__(self) -> tuple[type[getter], type[str, ...]]:
        """Reduce."""
        return self.__class__, self._attrs

    def __repr__(self) -> str:
        """Representation."""
        return self.__class__.__name__ + "(" + ",".join(f"{i}={getattr(self, i)!r}" for i in self._attrs) + ")"


class LetterCounter:
    """Letter Counter generator function. This way, each time you call next() on the generator.

    It will yield the next counter value. We will also remove the maximum counter check

    Examples:
        >>> from nodeps import LetterCounter
        >>>
        >>> c = LetterCounter("Z")
        >>> assert c.increment() == 'AA'
    """

    def __init__(self, start: str = "A") -> None:
        """Init."""
        self.current_value = [string.ascii_uppercase.index(v) for v in start[::-1]]

    def increment(self) -> str:
        """Increments 1.

        Exaamples:
            >>> from nodeps import LetterCounter
            >>>
            >>> c = LetterCounter('BWDLQZZ')
            >>> assert c.increment() == 'BWDLRAA'
            >>> assert c.increment() == 'BWDLRAB'

        Returns:
            str
        """
        for i in range(len(self.current_value)):
            # If digit is less than Z, increment and finish
            if self.current_value[i] < 25:  # noqa: PLR2004
                self.current_value[i] += 1
                break
            # Otherwise, set digit to A (0) and continue to next digit
            self.current_value[i] = 0
            # If we've just set the most significant digit to A,
            # we need to add another 'A' at the most significant end
            if i == len(self.current_value) - 1:
                self.current_value.append(0)
                break
        # Form the string and return
        return "".join(reversed([string.ascii_uppercase[i] for i in self.current_value]))


class NamedtupleMeta(metaclass=abc.ABCMeta):
    """Namedtuple Metaclass.

    Examples:
        >>> import collections
        >>> from nodeps import NamedtupleMeta
        >>>
        >>> named = collections.namedtuple('named', 'a', defaults=('a', ))
        >>>
        >>> assert isinstance(named(), NamedtupleMeta) == True
        >>> assert isinstance(named(), tuple) == True
        >>>
        >>> assert issubclass(named, NamedtupleMeta) == True
        >>> assert issubclass(named, tuple) == True
    """

    _fields: tuple[str, ...] = ()
    _field_defaults: dict[str, Any] = {}  # noqa: RUF012

    @abc.abstractmethod
    def _asdict(self) -> dict[str, Any]:
        return {}

    # noinspection PyPep8Naming
    @classmethod
    def __subclasshook__(cls, C: type) -> bool:  # noqa: N803
        """Subclass hook."""
        if cls is NamedtupleMeta:
            return (hasattr(C, "_asdict") and callable(C._asdict)) and all(
                [issubclass(C, tuple), hasattr(C, "_fields"), hasattr(C, "_field_defaults")]
            )
        return NotImplemented


class Noset:
    """Marker object for globals not initialized or other objects.

    Examples:
        >>> from nodeps import NOSET
        >>>
        >>> name = Noset.__name__.lower()
        >>> assert str(NOSET) == f'<{name}>'
        >>> assert repr(NOSET) == f'<{name}>'
        >>> assert repr(Noset("test")) == f'<test>'
    """

    name: str
    __slots__ = ("name",)

    def __init__(self, name: str = ""):
        """Init."""
        self.name = name if name else self.__class__.__name__.lower()

    def __hash__(self) -> int:
        """Hash."""
        return hash(
            (
                self.__class__,
                self.name,
            )
        )

    def __reduce__(self) -> tuple[type[Noset], tuple[str]]:
        """Reduce."""
        return self.__class__, (self.name,)

    def __repr__(self):
        """Repr."""
        return self.__str__()

    def __str__(self):
        """Str."""
        return f"<{self.name}>"


NOSET = Noset()
