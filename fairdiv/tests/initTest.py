from fairdiv import *
import math


@mem_cache(cache_size=10)
def cacheTest(x):
    return x*x


if __name__ == "__main__":

    args = range(1000)
    for i in args:
        cache_content = set([(args[i-j], ) for j in range(10) if i-j>=0])
        cacheTest(i)
        actual_cache_content = set(key for key in Database._mem_cache['cacheTest'])
        assert actual_cache_content == cache_content

    for i in range(8):
        assert len(Utils.generate_possible_problems(i+2)) == math.factorial(i+2)
        Utils.generate_possible_problems(i+2, True)
    for j in range(9):
        number_of_goods = (j+1) * 2

        print("testing with " + str(number_of_goods))
        goods = [Good(str(i)) for i in range(number_of_goods)]

        even_goods = [goods[i] for i in range(number_of_goods) if i % 2 == 0]
        odd_goods = [goods[i] for i in range(number_of_goods) if i % 2 == 1]

        a1 = Agent("agent1", goods[:])
        a2 = Agent("agent2", goods[::-1])
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

        assert max_min_rank([a1, a2], goods) == number_of_goods//2

        assert a1.is_ordinally_less(odd_goods)
        assert not a1.is_ordinally_less(even_goods)
        assert a2.is_ordinally_less(even_goods)
        assert not a2.is_ordinally_less(odd_goods)
