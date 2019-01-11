# -*- coding: utf-8 -*-


class Agent(object):
    """
    An agent with a name & ordinal preferences over goods.
    The rank of a good is given by its index in the pref list attribute
    """

    def __init__(self, name, pref=None):
        """
        Initializes an agent
        :param name: the agent's name
        """
        self._pref = []
        self.name = name
        if pref is not None:
            self._pref = pref

    @property
    def preferences(self):
        """
        Retrieves the agent's ordinal preferences.
        The returned list is a copy, so it can be manipulated freely.
        The rank of a good is given by its index in the pref list attribute
        :return:
        """
        return self._pref[:]

    @preferences.setter
    def preferences(self, value):
        """
        Sets the preferences of the agent
        :param value: An array of goods, from most preferred good to less preferred one
        :return:
        """
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

    def _get_good(self, rank, goods=None):
        """
        Retrieves a good among an iterable of goods given its rank
        :param rank: The rank of the desired good
        :param goods: an iterable of goods
        :return: The good with the given rank among the given goods.
                 If the rank is negative, from the less preferred item.
                 Returns None if the desired rank is over the goods iterable size
        """
        if goods is None:
            goods = self._pref[:]

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

    def top(self, goods=None):
        """
        Returns the most preferred good to the agent among an iterable of goods
        :param goods: an iterable of goods
        :return: The most preferred good for the agent
        """
        return self._get_good(1, goods)

    def sb(self, goods=None):
        """
        Returns the second most preferred good to the agent among an iterable of goods
        :param goods: an iterable of goods
        :return: The second most preferred good to the agent.
        """
        return self._get_good(2, goods)

    def last(self, goods=None):
        """
        Returns the less preferred good to the agent among an iterable of goods
        :param goods: an iterable of goods
        :return: the less preferred good to the agent
        """
        return self._get_good(-1, goods)

    def h(self, goods, l):
        """
        :param goods: an iterable of goods
        :param l: a rank
        :return: returns a list containing the goods (among the given one) that are ranked 'l' or better.
        """
        return [good for good in self._pref if good in goods and self.rank(good) <= l]

    def rank(self, good):
        """
        return the rank of a good for the agent
        :param good: a good
        :return: the good's rank
        """
        return self._pref.index(good)+1


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
    return k

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
