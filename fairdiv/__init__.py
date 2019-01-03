# -*- coding: utf-8 -*-


class Agent(object):
    """
    An agent.
    """

    def __init__(self, name):
        self._pref = []
        self.name = name

    @property
    def preferences(self):
        return self._pref[:]

    @preferences.setter
    def preferences(self, value):
        self._pref = value

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.preferences == other.preferences
        )

    def __hash__(self):
        return self.name.__hash__()

    def _get_good(self, rank, goods):
        pref = self._pref
        if rank < 0:
            rank = -rank
            pref = self._pref[::-1]
        for good in pref:
            if good in goods:
                rank -= 1
                if rank == 0:
                    return good
        return None

    def top(self, goods):
        return self._get_good(1, goods)

    def sb(self, goods):
        return self._get_good(2, goods)

    def last(self, goods):
        return self._get_good(-1, goods)

    def h(self, goods, l):
        return [good for good in self._pref[:l] if good in goods]

    def rank(self, good):
        return self._pref.index(good)


class Good(object):
    """
    A good (also called item) which is indivisible.
    """

    def __init__(self, name=''):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.name == other.name
        )

    def __hash__(self):
        return self.name.__hash__()


def max_min_rank(agents, goods):
    k = 0
    for good in goods:
        best_rank = len(goods)
        for agent in agents:
            rank = agent.rank(good)
            if rank <= best_rank:
                best_rank = rank
        if k <= best_rank:
            k = best_rank
    return k+1