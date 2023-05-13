processed = []


def my_fancy_iterator(start, end):
    pass


if __name__ == '__main__':
    it = my_fancy_iterator(0, 100)
    for i in range(10):
        next(it)

    assert processed == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
