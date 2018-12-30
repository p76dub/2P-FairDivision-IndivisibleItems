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


def is_max_min(alloc, allocs, agents):
    left = max([max([agents[i].preferences.index(item) for item in a]) for i, a in enumerate(
        alloc)])
    right = min([max([max([agents[i].preferences.index(item) for item in a]) for i, a in enumerate(
        current)]) for
                 current in allocs])
    return left == right
