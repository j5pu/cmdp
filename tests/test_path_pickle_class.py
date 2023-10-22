from nodeps import Path


class A:
    a = 1


def test_path_pickle_class():
     _ = Path.pickle(A)
     assert Path.pickle(name=A) == A

     assert Path.pickle(name=A, rm=True) is None