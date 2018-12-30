# -*- coding: utf-8 -*-
import itertools

from properties import is_pareto, is_envy_free, is_max_min


def original_sequential(agents, goods):
    """
    Use the Original Sequential Algorithm to compute a fair division of provided goods.
    :param agents: The agents with their preferences over provided goods
    :param goods: the goods
    :return: a set of possible allocations
    """
    assert len(agents) == 2
    assert len(goods) % 2 == 0

    allocations = set()

    def inner(z, u, l):
        if len(u) == 0:
            allocations.add((tuple(z[0]), tuple(z[1])))
            return

        ha_l = agents[0].preferences[:l]
        hb_l = agents[1].preferences[:l]
        found = False

        for i, j in itertools.combinations(u, 2):
            v = [good for good in u if good != i and good != j]

            if i in ha_l and j in hb_l:
                za, zb = z[0][:], z[1][:]
                za.append(i)
                zb.append(j)

                found = True
                inner((za, zb), v, l+1)

            if j in ha_l and i in hb_l:
                za, zb = z[0][:], z[1][:]
                za.append(j)
                zb.append(i)

                found = True
                inner((za, zb), v, l+1)

        if not found:
            inner(z, u, l+1)

    inner(([], []), goods, 1)
    return allocations


def generate_all_allocations(goods):
    """
    Generate all possible allocations. I think it should generate all different permutations
    :param goods: all considered goods
    :return: allocation for 2 agents
    """
    allocs = list(itertools.combinations(goods, len(goods) // 2))
    return [(tuple(alloc), tuple([g for g in goods if g not in alloc])) for alloc in allocs]


if __name__ == '__main__':
    from fairdiv import Agent, Good

    goods = [Good(str(i)) for i in range(4)]

    a1 = Agent("A")
    a1.preferences = [
        goods[0], goods[2], goods[1], goods[3]
    ]

    a2 = Agent("B")
    a2.preferences = [
        goods[1], goods[3], goods[0], goods[2]
    ]

    allocs = original_sequential((a1, a2), goods)
    all_allocs = generate_all_allocations(goods)

    print("Allocations found :")
    for i, alloc in enumerate(allocs):
        print("\tAllocation n°{}".format(i+1))
        print("\t\t Agent {}: {}".format(a1, alloc[0]))
        print("\t\t Agent {}: {}".format(a2, alloc[1]))
        print("\t\t Pareto optimal: {}".format(is_pareto(alloc, all_allocs, (a1, a2))))
        print("\t\t Envy-free: {}".format(is_envy_free(alloc, (a1, a2))))
        print("\t\t Max-min: {}".format(is_max_min(alloc, allocs, (a1, a2))))
