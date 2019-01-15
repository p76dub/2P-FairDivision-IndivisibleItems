from fairdiv import *


if __name__ == "__main__":
    # Should be an even number at least equal to 10
    number_of_goods = 20

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
    assert a1.sb(even_goods) == goods[2]
    assert a1.last(even_goods) == goods[number_of_goods-2]
    assert a2.top(even_goods) == goods[number_of_goods-2]
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
