from fairdiv import *
from funcache import MemoryCache
from multiprocessing import Pool
import math


@MemoryCache(cache_size=300)
def cache_test(x):
    return x*x


def test(i):
    return cache_test(i)


if __name__ == "__main__":

    args = range(1000)
    pool = Pool(2)
    MemoryCache.enable_multiprocessing(pool, 2)
    FileCache.enable_multiprocessing(pool, 2)
    pool.map(test, range(200))
    for i in range(7):
        assert len(Problem.generate_possible_problems(i+2)) == math.factorial(i+2)
    for j in range(10):
        number_of_goods = (j+1) * 2

        print("testing with " + str(number_of_goods))
        goods = [Good(str(i)) for i in range(number_of_goods)]

        even_goods = [goods[i] for i in range(number_of_goods) if i % 2 == 0]
        odd_goods = [goods[i] for i in range(number_of_goods) if i % 2 == 1]

        a1 = Agent("agent1", goods[:])
        a2 = Agent("agent2", goods[::-1])
        problem = Problem((a1, a2), goods)
        assert a1.top() == goods[0]
        assert a1.sb() == goods[1]
        assert a1.last() == goods[number_of_goods-1]
        assert a2.top() == goods[number_of_goods-1]
        assert a2.sb() == goods[number_of_goods-2]
        assert a2.last() == goods[0]

        assert a1.top(even_goods) == goods[0]
        if number_of_goods >= 4:
            assert a1.sb(even_goods) == goods[2]
        assert a1.last(even_goods) == goods[number_of_goods-2]
        assert a2.top(even_goods) == goods[number_of_goods-2]
        if number_of_goods >= 4:
            assert a2.sb(even_goods) == goods[number_of_goods-4]
        assert a2.last(even_goods) == goods[0]

        assert a1.rank(a1.top()) == 1
        assert a2.rank(a1.top()) == number_of_goods

        assert a1.h(even_goods, number_of_goods//2) == [goods[i] for i in range(number_of_goods) if i % 2 == 0 and i < number_of_goods//2]
        assert a2.h(even_goods, number_of_goods//2) == [goods[i] for i in reversed(range(number_of_goods)) if i % 2 == 0 and i >= number_of_goods//2]

        assert problem.max_min_rank() == number_of_goods//2

        assert a1.is_ordinally_less(odd_goods)
        assert not a1.is_ordinally_less(even_goods)
        assert a2.is_ordinally_less(even_goods)
        assert not a2.is_ordinally_less(odd_goods)
