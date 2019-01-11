from fairdiv import *

if __name__ == "__main__":
    number_of_goods = 20

    goods = [Good(str(i)) for i in range(number_of_goods)]

    even_goods = [goods[i] for i in range(number_of_goods) if i%2==0]

    a1 = Agent("agent1", goods[:])
    a2 = Agent("agent2", goods[::-1])
    assert a1.top() == goods[0]
    assert a1.sb() == goods[1]
    assert a1.last() == goods[19]
    assert a2.top() == goods[19]
    assert a2.sb() == goods[18]
    assert a2.last() == goods[0]

    assert a1.top(even_goods) == goods[0]
    assert a1.sb(even_goods) == goods[2]
    assert a1.last(even_goods) == goods[18]
    assert a2.top(even_goods) == goods[18]
    assert a2.sb(even_goods) == goods[16]
    assert a2.last(even_goods) == goods[0]

    assert a1.rank(a1.top()) == 1
    assert a2.rank(a1.top()) == number_of_goods

    assert a1.h(even_goods, 10) == [goods[0], goods[2], goods[4], goods[6], goods[8]]
    assert a2.h(even_goods, 10) == [goods[18], goods[16], goods[14], goods[12], goods[10]]

    assert max_min_rank([a1, a2], goods) == 10
