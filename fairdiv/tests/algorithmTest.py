def printall(func):
    def inner(*args, **kwargs):
        print('Arguments for args: {}'.format(args))
        print('Arguments for kwargs: {}'.format(kwargs))
        print(func.__qualname__)
        return func(*args, **kwargs)
    return inner

@printall
def test():
    print("hello world")


class Test:
    @staticmethod
    def test():
        print("Hello new world")


if __name__ == "__main__":
    test()
