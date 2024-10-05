class Baz:
    def __new__(cls, x, y):
        pass


if __name__ == '__main__':
    assert Baz.__new__.__annotations__ == {}
    obj = Baz.__dict__['__new__']
    assert isinstance(obj, staticmethod)
    getattr(obj, '__annotations__', None)
    obj.__annotations__
