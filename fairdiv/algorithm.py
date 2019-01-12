# -*- coding: utf-8 -*-
import itertools

from properties import is_pareto, is_envy_free, is_max_min
from fairdiv import Agent, Good, max_min_rank


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

        ha_l = [p for p in agents[0].preferences[:l] if p in u]
        hb_l = [p for p in agents[1].preferences[:l] if p in u]
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


def restricted_sequential(agents, goods):
    """
    Use the Restricted Sequential Algorithm to compute a fair division of provided goods.
    :param agents: The agents with their preferences over provided goods
    :param goods: the goods
    :return: a set of possible allocations
    """
    assert len(agents) == 2
    assert len(goods) % 2 == 0

    allocations = set()

    def inner(z, u, l):
        """
        Follows the allocation process from a given point. Branches if necessary.
        Puts the allocations it finds in the allocations set defined above
        :param z: The allocation currently working on
        :param u: The list of unallocated items
        :param l: The max rank of goods to consider
        :return:
        """
        if len(u) == 0:
            allocations.add((tuple(z[0]), tuple(z[1])))
            return

        ha_l = [p for p in agents[0].preferences[:l] if p in u]
        hb_l = [p for p in agents[1].preferences[:l] if p in u]

        if ha_l[0] != hb_l[0]:
            za, zb = z[0][:], z[1][:]
            v = [good for good in u if good != ha_l[0] and good != hb_l[0]]
            za.append(ha_l[0])
            zb.append(hb_l[0])
            inner((za, zb), v, l+1)
        else:
            if len(ha_l) > 1:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != ha_l[1] and good != hb_l[0]]
                za.append(ha_l[1])
                zb.append(hb_l[0])
                inner((za, zb), v, l + 1)
            if len(hb_l) > 1:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != ha_l[0] and good != hb_l[1]]
                za.append(ha_l[0])
                zb.append(hb_l[1])
                inner((za, zb), v, l + 1)

    inner(([], []), goods, 1)
    return allocations


def singles_doubles(agents, goods):
    allocations = set()

    k = max_min_rank(agents, goods)

    ha_k = set(agents[0].h(goods, k))
    hb_k = set(agents[1].h(goods, k))

    za = list(ha_k.difference(hb_k))
    zb = list(hb_k.difference(ha_k))

    u = list(ha_k.intersection(hb_k))

    def inner(z, u):
        if len(u) == 0:
            allocations.add((tuple(z[0]), tuple(z[1])))
            return

        top_a = agents[0].top(u)
        top_b = agents[1].top(u)

        sb_a = agents[0].sb(u)
        sb_b = agents[0].sb(u)

        if top_a != top_b:
            za, zb = z[0][:], z[1][:]
            v = [good for good in u if good != top_a and good != top_b]
            za.append(top_a)
            zb.append(top_b)
            inner((za, zb), v)

        za, zb = z[0][:], z[1][:]
        za.append(top_a)
        zb.append(sb_b)
        if is_envy_free((za, zb), agents):
            v = [good for good in u if good != top_a and good != sb_b]
            inner((za, zb), v)

        za, zb = z[0][:], z[1][:]
        za.append(sb_a)
        zb.append(top_b)
        if is_envy_free((za, zb), agents):
            v = [good for good in u if good != sb_a and good != top_b]
            inner((za, zb), v)

    inner((za, zb), u)
    return allocations


def bottom_up(agents, goods):
    """
    Use the bottom-up algorithm to calculate allocations.
    :param agents:
    :param goods:
    :return:
    """
    def inner(m, z, u):
        if len(u) == 0:
            return z

        g = agents[m].last(u)
        z[(m+1) % 2].append(g)
        u.remove(g)
        return inner((m+1) % 2, z, u)

    u = goods[:]
    return inner(0, ([], []), u[:]), inner(1, ([], []), u)


def trump_algorithm(agents, goods):  # Fixme: NOT WORKING
    """
    Use the Trump algorithm to compute a fair division of provided goods.
    :param agents: agents (to get preferences)
    :param goods: all considered goods
    :return: all possible allocations
    """

    def inner(agents):  # On purpose
        u = goods[:]
        alloc = ([], [])

        for l in range(1, len(goods) + 1, 2):
            for i, agent in enumerate(agents):
                hm_l = [p for p in agents[0].preferences[:l] if p in u]

                if len(hm_l) == 0:
                    return

                good = sorted(hm_l, key=lambda x: agents[(i+1) % 2].preferences.index(x))[-1]

                alloc[i].append(good)
                u.remove(good)

    return inner(agents)#, inner((agents[1], agents[0]))  # Each agent starts


def generate_all_allocations(goods):
    """
    Generate all possible allocations. I think it should generate all different permutations
    :param goods: all considered goods
    :return: allocation for 2 agents
    """
    # Generate allocations for one agent
    allocs = list(itertools.combinations(goods, len(goods) // 2))

    # Generate all permutations
    p_allocs = []
    for alloc in allocs:
        p_allocs.extend(itertools.permutations(alloc))

    c_allocs = []
    for alloc in p_allocs:
        other = [g for g in goods if g not in alloc]
        perms = itertools.permutations(other)
        for perm in perms:
            c_allocs.append((tuple(alloc), tuple(perm)))

    return c_allocs


if __name__ == '__main__':

    goods = [Good(str(i)) for i in range(4)]

    a1 = Agent("A")
    a1.preferences = [
        goods[0], goods[2], goods[1], goods[3]
    ]

    a2 = Agent("B")
    a2.preferences = [
        goods[1], goods[3], goods[0], goods[2]
    ]

    # allocs = singles_doubles((a1, a2), goods)
    # allocs = original_sequential((a1, a2), goods)
    # allocs = trump_algorithm((a1, a2), goods)
    allocs = bottom_up((a1, a2), goods)
    all_allocs = generate_all_allocations(goods)

    print("Allocations found :")
    for i, alloc in enumerate(allocs):
        print("\tAllocation n°{}".format(i+1))
        print("\t\t Agent {}: {}".format(a1, alloc[0]))
        print("\t\t Agent {}: {}".format(a2, alloc[1]))
        print("\t\t Pareto optimal: {}".format(is_pareto(alloc, all_allocs, (a1, a2))))
        print("\t\t Envy-free: {}".format(is_envy_free(alloc, (a1, a2))))
        print("\t\t Max-min: {}".format(is_max_min(alloc, all_allocs, (a1, a2))))
