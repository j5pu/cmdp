import os
from pathlib import Path

from nodeps import envbash

tests_envbash = Path(__file__).parent / "env.bash"
keys = [f'TEST_{_i}' for _i in ['MACOS', 'LOGNAME', 'LOGNAMEHOME', 'ROOTHOME', 'LOGGEDINUSER',
                                'LOGNAMEREALNAME', 'MULTILINE']]

EnvironOS = type(os.environ)


def check(env):
    for i in keys:
        assert env.get(i) is not None
        del env[i]


def test_envbash():
    rv = envbash(tests_envbash)
    assert isinstance(rv, EnvironOS)
    assert id(rv) == id(os.environ)
    check(rv)


def test_envbash_into():
    into = {}
    rv = envbash(tests_envbash, into=into)
    assert not isinstance(rv, EnvironOS)
    assert id(into) == id(rv)
    check(rv)


def test_envbash_new():
    rv = envbash(tests_envbash, new=True)
    assert not isinstance(rv, EnvironOS)
    rv_copy = rv.copy()
    check(rv)

    for i in os.environ:
        assert i in rv_copy if i in keys else i not in rv_copy


def test_envbash_override():
    rv = envbash(tests_envbash, override=False)
    assert not isinstance(rv, EnvironOS)
    assert id(rv) != id(os.environ)
    check(rv)
