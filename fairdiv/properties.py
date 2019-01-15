# -*- coding: utf-8 -*-


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