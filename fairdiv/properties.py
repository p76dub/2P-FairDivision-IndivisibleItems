# -*- coding: utf-8 -*-
import functools
from cacheUtils import cache


@cache
def is_pareto(X, A, M):
    """
    :param X: An allocation
    :param A: The possible allocations
    :param M: The agents
    :return: True if the allocation verifies the pareto property
    """
    xa = sorted([M[0].rank(g) for g in X[0]])
    xb = sorted([M[1].rank(g) for g in X[1]])

    for x in A:
        if X == x:
            continue

        ya = x[0]
        yb = x[1]

        ra = sorted([M[0].rank(i) for i in ya])
        rb = sorted([M[1].rank(i) for i in yb])

        # Check agent A
        higher = False
        lower = False
        result = 0

        for i in range(len(xa)):
            if xa[i] > ra[i]:
                lower = True
            elif xa[i] < ra[i]:
                higher = True

        if higher and not lower:
            result += 1
        elif lower and not higher:
            result -= 1

        higher = False
        lower = False
        for i in range(len(ya)):
            if xb[i] > rb[i]:
                lower = True
            elif xb[i] < rb[i]:
                higher = True

        if higher and not lower:
            result += 1
        elif lower and not higher:
            result -= 1

        if result < 0:
            return False

    return True


@cache
def is_envy_free(X, M):
    """
    :param X: An allocation
    :param M: The agents
    :return: True if the allocation is envy free
    """
    xa = sorted([M[0].rank(i) for i in X[0]])
    xb = sorted([M[1].rank(i) for i in X[1]])

    ya = sorted([M[1].rank(i) for i in X[0]])
    yb = sorted([M[0].rank(i) for i in X[1]])

    for i in range(len(xa)):
        if xa[i] > ya[i]:  # Not sure if it is correct
            return False

    for i in range(len(xb)):
        if xb[i] > yb[i]:  # Not sure if it is correct
            return False

    return True


@cache
def is_pareto_ordinally(X, A, M):
    """
    :param X: An allocation
    :param A: The possible allocations
    :param M: The agents
    :return: True if the allocation verifies the ordinally pareto property
    """
    found = False
    i = 0

    while not found and i < len(A):
        for j in range(len(M)):
            found = found or M[j].is_ordinally_less(X[j], A[i][j])

    return not found


@cache
def is_envy_free_ordinally(alloc, agents):
    """
    :param alloc: An allocation
    :param agents: The agents
    :return: True if the allocation verifies the ordinally envy free property
    """
    if agents[0].is_ordinally_less(alloc[0]) or agents[1].is_ordinally_less(alloc[1]):
        return False
    return True


@cache
def is_max_min(X, A, M):
    """
    :param X: An allocation
    :param A: The possible allocations
    :param M: The agents
    :return: True if the allocation verifies the max min property
    """
    left = max([max([m.rank(i) for i in X[ind]]) for ind, m in enumerate(M)])
    right = min([max(
        [max([m.rank(i) for i in Y[ind]]) for ind, m in enumerate(M)]
    ) for Y in A])
    return left == right


@cache
def is_borda_pareto(X, A, M):
    """
    Test if allocation X is Borda pareto given agents m and all available allocations

    :param X: allocation to test
    :param A: all available allocations for current problem
    :param M: the agents
    :return: True if X is Borda pareto, 
    """
    ba = M[0].borda(X[0])
    bb = M[1].borda(X[1])

    for Y in A:
        bai = M[0].borda(Y[0])
        bbi = M[1].borda(Y[1])

        if (bai > ba and bbi >= bb) or (bbi > bb and bai >= ba):
            return False

    return True


@cache
def is_maximal_borda_sum(X, A, M):
    """
    Test if an allocation X is maximal-Borda-sum given agents m and all available allocations

    :param X: allocation to test
    :param A: all available allocations for the current problem
    :param M: the agents
    :return: True if X is maximal Borda sum
    """
    return sum([M[i].borda(X[i]) for i in range(len(M))]) == max(
        [sum([M[i].borda(Y[i]) for i in range(len(M))]) for Y in A]
    )


@cache
def is_borda_envy_free(X, M):
    """
    Test if the provided allocation X is borda_envy_free
    :param X: the allocation to test
    :param M: the agents
    :return: True if the allocation is Borda-envy-free, else False
    """
    return M[0].borda(X[0]) >= M[0].borda(X[1]) and M[1].borda(X[1]) >= M[1].borda(X[0])


@cache
def is_borda_max_min(X, A, M):
    """
    Test if an allocation is Borda max-min.

    :param X: allocation
    :param A: all available allocations
    :param M: agents
    :return: True if allocation is Borda max-min, else False
    """
    left = min([M[i].borda(X[i]) for i in range(len(M))])
    right = max([min([M[i].borda(Y[i]) for i in range(len(M))]) for Y in A])
    return left == right


@cache
def is_borda_nash(X, A, M):
    """
    Test if an allocation is Borda Nash, ie M[0].borda(X[0]) * M[1].borda(X[1]) is the best among
    other allocations.

    :param X: allocation
    :param A: all available allocations
    :param M: agents
    :return: True if allocation is Borda-Nash, else False
    """
    left = functools.reduce(lambda a, b: a * b, [M[i].borda(X[i]) for i in range(len(M))])
    right = max(
        [functools.reduce(lambda a, b: a * b, [M[i].borda(Y[i]) for i in range(len(M))]) for Y in A]
    )
    return left == right


@cache
def is_borda_egalitarian(X, M):
    """
    Test if the allocation is Borda egalitarian, meaning that M[0].borda(X[0]) >= 1/2 * M[
    0].borda(X[0] + X[1]) and M[1].borda(X[1]) >= 1/2 * M[1].borda(X[0] + X[1])

    :param X: allocation you want to test
    :param M: agents
    :return: True if allocation is Borda-Egalitarian, else False
    """
    # Get all goods
    goods = []
    for am in X:
        goods.extend(am)

    # Compute result
    return functools.reduce(
        lambda a, b: a and b,
        [M[i].borda(X[i]) >= 1/2 * M[i].borda(goods) for i in range(len(M))]
    )


if __name__ == '__main__':
    import fairdiv

    # Create some constants
    NUMBER_OF_GOODS = 4

    # Create items
    items = [fairdiv.Good(str(i)) for i in range(NUMBER_OF_GOODS)]

    # Create agents. We will consider that item's number is their rank in preferences of the first agent
    agents = [
        fairdiv.Agent(name="A", pref=items[:]),
        fairdiv.Agent(name="B", pref=[items[0], items[2], items[1], items[3]])
    ]

    # Manipulate path
    import os
    import sys

    #sys.path.insert(0, os.path.join(os.getcwd(), 'fairdiv'))

    # Import algorithms
    import fairdiv.algorithm as algorithm

    # Use bottom-up to compute two allocations
    (x1, x2) = algorithm.bottom_up(agents, items)
    print(x1)
    print(x2)

    # Generate all allocations for our problem
    A = list(fairdiv.Allocation.generate_all_allocations(agents, items))
    print(A)

    # Use them in properties
    print(is_pareto(x1, A, agents))
    print(is_pareto(x2, A, agents))
    print(is_pareto(
        fairdiv.Allocation(
            agents[0], [items[0], items[2]],
            agents[1], [items[1], items[3]]
        ),
        A,
        agents
    ))
