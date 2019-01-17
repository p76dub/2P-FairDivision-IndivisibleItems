from fairdiv import *
import itertools
import pickle

from collections import Iterable


def test(a, b):
    return a, b


if __name__ == "__main__":
    alloc1 = ()
    alloc2 = ()
    print(Database.get(Utils.get_possible_injections, (), ()))