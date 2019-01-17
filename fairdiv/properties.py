# -*- coding: utf-8 -*-
import functools


def is_pareto(alloc, allocs, agents):
    xa = sorted([agents[0].preferences.index(i) for i in alloc[0]])
    xb = sorted([agents[1].preferences.index(i) for i in alloc[1]])

    for ya, yb in allocs:
        if alloc == (ya, yb):
            continue

        ra = sorted([agents[0].preferences.index(i) for i in ya])
        rb = sorted([agents[1].preferences.index(i) for i in yb])

        higher = False
        lower = False
        for i in range(len(xa)):
            if xa[i] > ra[i]:
                higher = True
            elif xa[i] < ra[i]:
                lower = True

        if higher and not lower:
            return False

        for i in range(len(ya)):
            if xb[i] > rb[i]:
                higher = True
            elif xb[i] < rb[i]:
                lower = True

        if higher and not lower:
            return False

    return True


def is_envy_free(alloc, agents):
    xa = sorted([agents[0].preferences.index(i) for i in alloc[0]])
    xb = sorted([agents[1].preferences.index(i) for i in alloc[1]])

    ya = sorted([agents[1].preferences.index(i) for i in alloc[0]])
    yb = sorted([agents[0].preferences.index(i) for i in alloc[1]])

    for i in range(len(xa)):
        if xa[i] > ya[i]:  # Not sure if it is correct
            return False

    for i in range(len(xb)):
        if xb[i] > yb[i]:  # Not sure if it is correct
            return False

    return True


def is_max_min(X, A, M):
    left = max([max([m.preferences.index(i) for i in X[ind]]) for ind, m in enumerate(M)])
    right = min([max(
        [max([m.preferences.index(i) for i in Y[ind]]) for ind, m in enumerate(M)]
    ) for Y in A])
    return left == right


def is_borda_pareto(X, A, M):
    """
    Test if allocation X is Borda pareto given agents m and all available allocations
    :param X: allocation to test
    :param A: all available allocations for current problem§
    :param M: the agents
    :return: True if X is Borda pareto, 
    """
    ba = M[0].borda(X[0])
    bb = M[1].borda(X[1])

    for (Ai, Bi) in A:
        bai = M[0].borda(Ai)
        bbi = M[1].borda(Bi)

        if (bai > ba and bbi >= bb) or (bbi > bb and bai >= ba):
            return False

    return True


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


def is_borda_envy_free(X, M):
    """
    Test if the provided allocation X is borda_envy_free
    :param X: the allocation to test
    :param M: the agents
    :return: True if the allocation is Borda-envy-free, else False
    """
    return M[0].borda(X[0]) >= M[0].borda(X[1]) and M[1].borda(X[1]) >= M[1].borda(X[0])


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


def is_borda_nash(X, A, M):
    """
    Test if an allocation is Borda Nash.
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