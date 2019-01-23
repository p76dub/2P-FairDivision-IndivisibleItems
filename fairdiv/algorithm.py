# -*- coding: utf-8 -*-
import itertools
import fairdiv
from properties import is_envy_free


@fairdiv.cache
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

        ha_l = agents[0].h(u, l)
        hb_l = agents[1].h(u, l)
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
    return fairdiv.Allocation.get_allocations(agents, allocations)


@fairdiv.cache
def restricted_sequential(agents, goods):
    """
    Uses the Restricted Sequential Algorithm to compute a fair division of provided goods.
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
        top_a = agents[0].top(u)
        top_b = agents[1].top(u)
        branched = False
        if top_a != top_b:
            za, zb = z[0][:], z[1][:]
            v = [good for good in u if good != top_a and good != top_b]
            za.append(top_a)
            zb.append(top_b)
            inner((za, zb), v, l+1)
            branched = True
        else:
            ha_l = agents[0].h(u, l)
            hb_l = agents[1].h(u, l)
            if len(ha_l) > 1 and len(hb_l) > 0:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != ha_l[1] and good != hb_l[0]]
                za.append(ha_l[1])
                zb.append(hb_l[0])
                inner((za, zb), v, l + 1)
                branched = True
            if len(hb_l) > 1 and len(ha_l) > 0:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != ha_l[0] and good != hb_l[1]]
                za.append(ha_l[0])
                zb.append(hb_l[1])
                inner((za, zb), v, l + 1)
                branched = True
        if not branched:
            inner(z, u, l+1)
    inner(([], []), goods, 1)
    return fairdiv.Allocation.get_allocations(agents, allocations)

@fairdiv.cache
def singles_doubles(agents, goods):
    """
    Uses the singles doubles algorithm to compute fair divisions of provided goods
    :param agents: The agents with their preferences over provided goods
    :param goods: the goods
    :return: a set of possible allocations
    """
    allocations = set()

    k = fairdiv.max_min_rank(agents, goods)

    ha_k = set(agents[0].h(goods, k))
    hb_k = set(agents[1].h(goods, k))

    za = list(ha_k.difference(hb_k))
    zb = list(hb_k.difference(ha_k))
    
    u = list(ha_k.intersection(hb_k))

    def inner(z, u):
        """
                Follows the allocation process from a given point. Branches if necessary.
                Puts the allocations it finds in the allocations set defined above
                :param z: The allocation currently working on
                :param u: The list of unallocated items
                :return:
                """
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
    return fairdiv.Allocation.get_allocations(agents, allocations)

@fairdiv.cache
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

    return fairdiv.Allocation.get_allocations(agents, [
        inner(0, ([], []), u[:]),
        inner(1, ([], []), u)
    ])


@fairdiv.cache
def trump_algorithm(agents, goods):
    """
    Use the Trump algorithm to compute a fair division of provided goods.
    :param agents: agents (to get preferences)
    :param goods: all considered goods
    :return: all possible allocations
    """

    def inner(M):
        V = ([], [])
        U = goods[:]
        for l in range(1, len(goods), 2):
            for i, m in enumerate(M):
                hm_l = m.h(U, l)
                if len(hm_l) == 0:
                    return None
                item = M[(i+1) % 2].last(hm_l)
                U.remove(item)
                V[i].append(item)
        return V

    r1 = inner(agents)
    r2 = inner((agents[1], agents[0]))
    if r1 is None and r2 is None:
        return set()
    r2 = r2[1], r2[0] if r2 is not None else r2  # r2 was inverted
    return fairdiv.Allocation.get_allocations(agents, [r for r in (r1, r2) if r is not None])


if __name__ == '__main__':
    import os
    os.chdir('..')

    import fairdiv
    # Create some constants
    NUMBER_OF_GOODS = 8

    # Create items
    items = [fairdiv.Good(str(i + 1)) for i in range(NUMBER_OF_GOODS)]

    # Create agents. We will consider that item's number is their rank in preferences of the first agent
    agents = [
        fairdiv.Agent(name="A", pref=items[:]),
        fairdiv.Agent(name="B",
                      pref=[items[2], items[3], items[4], items[5], items[6], items[7], items[0],
                            items[1]])
    ]

    # Generate all allocations for the given problem
    A = list(fairdiv.Allocation.generate_all_allocations(agents, items))

    results = {
        "OS": original_sequential(agents, items),
        # "RS": restricted_sequential(agents, items),
        # "SD": singles_doubles(agents, items),
        # "BU": bottom_up(agents, items),
        # "TA": trump_algorithm(agents, items)
    }

    for k, v in results.items():
        print("{}: {}".format(k, v))
