# -*- coding: utf-8 -*-
import itertools
from properties import OrdinalEnvyFreeness
from fairdiv import Allocation, Problem
from funcache import FileCache


class Algorithm(object):
    """
    This class describes algorithms that solves fair division problems
    The subclasses just have to redefine the compute method
    """

    @staticmethod
    def compute(problem: Problem):
        """
        This method is meant to be redefined by subclasses
        :param problem: The fair division problem to solve
        :return: A collection of the allocations proposed by the algorithm
        """
        raise NotImplementedError


class OriginalSequential(Algorithm):
    """
    This class implements the OriginalSequential Algorithm
    """

    @staticmethod
    @FileCache()
    def compute(problem: Problem):
        """
            Use the Original Sequential Algorithm to compute a fair division of provided goods.
            :param problem:
            :return: a set of possible allocations
            """
        assert len(problem.agents) == 2
        assert len(problem.goods) % 2 == 0

        allocations = set()

        def inner(z, u, l):
            if len(u) == 0:
                allocations.add((tuple(z[0]), tuple(z[1])))
                return

            ha_l = problem.agents[0].h(u, l)
            hb_l = problem.agents[1].h(u, l)
            found = False

            for i, j in itertools.combinations(u, 2):
                v = [good for good in u if good != i and good != j]

                if i in ha_l and j in hb_l:
                    za, zb = z[0][:], z[1][:]
                    za.append(i)
                    zb.append(j)

                    found = True
                    inner((za, zb), v, l + 1)

                if j in ha_l and i in hb_l:
                    za, zb = z[0][:], z[1][:]
                    za.append(j)
                    zb.append(i)

                    found = True
                    inner((za, zb), v, l + 1)

            if not found:
                inner(z, u, l + 1)

        inner(([], []), problem.goods, 1)
        return Allocation.get_allocations(problem.agents, allocations)


class RestrictedSequential(Algorithm):
    """
    This class implements the Restricted Sequential Algorithm
    """

    @staticmethod
    @FileCache()
    def compute(problem: Problem):
        """
        Uses the Restricted Sequential Algorithm to compute a fair division of provided goods.
        :param problem:
        :return: a set of possible allocations
        """
        assert len(problem.agents) == 2
        assert len(problem.goods) % 2 == 0

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
            top_a = problem.agents[0].top(u)
            top_b = problem.agents[1].top(u)
            branched = False
            if top_a != top_b:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != top_a and good != top_b]
                za.append(top_a)
                zb.append(top_b)
                inner((za, zb), v, l + 1)
                branched = True
            else:
                ha_l = problem.agents[0].h(u, l)
                hb_l = problem.agents[1].h(u, l)
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
                inner(z, u, l + 1)

        inner(([], []), problem.goods, 1)
        return Allocation.get_allocations(problem.agents, allocations)


class SinglesDoubles(Algorithm):
    """
    This class implements the Singles-Doubles Algorithm
    """

    @staticmethod
    @FileCache()
    def compute(problem: Problem):
        """
            Uses the singles doubles algorithm to compute fair divisions of provided goods
            :param problem:
            :return: a set of possible allocations
            """
        allocations = set()

        k = problem.max_min_rank()

        ha_k = set(problem.agents[0].h(problem.goods, k))
        hb_k = set(problem.agents[1].h(problem.goods, k))

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

            top_a = problem.agents[0].top(u)
            top_b = problem.agents[1].top(u)

            sb_a = problem.agents[0].sb(u)
            sb_b = problem.agents[1].sb(u)

            if top_a != top_b:
                za, zb = z[0][:], z[1][:]
                v = [good for good in u if good != top_a and good != top_b]
                za.append(top_a)
                zb.append(top_b)
                inner((za, zb), v)

            if top_a != sb_b:
                za, zb = z[0][:], z[1][:]
                za.append(top_a)
                zb.append(sb_b)
                if OrdinalEnvyFreeness.check((za, zb), problem.agents):
                    v = [good for good in u if good != top_a and good != sb_b]
                    inner((za, zb), v)

            if sb_a != top_b:
                za, zb = z[0][:], z[1][:]
                za.append(sb_a)
                zb.append(top_b)
                if OrdinalEnvyFreeness.check((za, zb), problem.agents):
                    v = [good for good in u if good != sb_a and good != top_b]
                    inner((za, zb), v)

        inner((za, zb), u)
        return Allocation.get_allocations(problem.agents, allocations)


class BottomUp(Algorithm):
    """
    This class implements the Bottom Up Algorithm
    """

    @staticmethod
    @FileCache()
    def compute(problem: Problem):
        """
        Use the bottom-up algorithm to calculate allocations.
        :param problem:
        :return:
        """

        def inner(m, z, u):
            if len(u) == 0:
                return z

            g = problem.agents[m].last(u)
            z[(m + 1) % 2].append(g)
            u.remove(g)
            return inner((m + 1) % 2, z, u)

        u = list(problem.goods[:])

        return Allocation.get_allocations(problem.agents, [
            inner(0, ([], []), u[:]),
            inner(1, ([], []), u)
        ])


class Trump(Algorithm):
    """
    This class implements the Trump Algorithm
    """

    @staticmethod
    @FileCache()
    def compute(problem: Problem):
        """
        Use the Trump algorithm to compute a fair division of provided goods.
        :param problem:
        :return: all possible allocations
        """

        def inner(M):
            V = ([], [])
            U = set(problem.goods[:])
            for l in range(1, len(problem.goods), 2):
                for i, m in enumerate(M):
                    hm_l = m.h(U, l)
                    if len(hm_l) == 0:
                        return None
                    item = M[(i + 1) % 2].last(hm_l)
                    U.remove(item)
                    V[i].append(item)
            return V

        r1 = inner(problem.agents)
        r2 = inner((problem.agents[1], problem.agents[0]))
        if r1 is None and r2 is None:
            return set()
        r2 = r2[1], r2[0] if r2 is not None else r2  # r2 was inverted
        return Allocation.get_allocations(problem.agents, [r for r in (r1, r2) if r is not None])


if __name__ == '__main__':
    import os

    os.chdir('..')

    import fairdiv
    import fairdiv.properties as props

    # Create some constants
    NUMBER_OF_GOODS = 4

    # Create items
    items = [fairdiv.Good(str(i + 1)) for i in range(NUMBER_OF_GOODS)]

    # Create agents. We will consider that item's number is their rank in preferences of the first agent
    agents = [
        fairdiv.Agent(name="A", pref=items[:]),
        fairdiv.Agent(name="B", pref=[items[0], items[2], items[1], items[3]])
    ]

    problem = Problem(agents, items)

    # Generate all allocations for the given problem
    A = list(fairdiv.Allocation.generate_all_allocations(agents, items))
    for alloc in A:
        print('{} -> {}'.format(alloc, props.is_envy_free_ordinally(alloc, agents)))

    result = OriginalSequential.compute(problem)
    print("OS: {}".format(result))

    TR = Trump.compute(problem)
    print("TR: {}".format(TR))
    for alloc in TR:
        print(props.is_pareto_ordinally(alloc, A, agents))
