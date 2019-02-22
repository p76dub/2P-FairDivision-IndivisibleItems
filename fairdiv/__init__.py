# -*- coding: utf-8 -*-
import collections
import itertools
from functools import total_ordering
from funcache import MemoryCache, FileCache


class Utils(object):
    """
    Groups some utility methods
    """
    @staticmethod
    @MemoryCache(cache_size=1000)
    def get_possible_injections(alloc1, alloc2):
        """
        Returns a list of possible mappings from alloc1 to alloc2.
        Note that this method's results are stored in the memory cache.
        :param alloc1:
        :param alloc2:
        :return:
        """
        return [[j for j in map(lambda x, y: (x, y), alloc1, i)] for i in itertools.permutations(alloc2)]


@total_ordering
class Good(object):
    """
    A good (also called item) which is indivisible.
    """

    def __init__(self, name=''):
        """
        :param name:
        :type name: str
        """
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

    def __lt__(self, other):
        return self.name.__lt__(other.name)

    def __hash__(self):
        return self.name.__hash__()


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
        :type good: Good
        :return: the good's rank
        """
        return self._pref.index(good)+1

    def compare_goods(self, good1, good2):
        """
        compares two goods using the current agent's preferences.
        :param good1: a good.
        :param good2: a good.
        :return: True if :param:`good1` is strictly better than :param:`good2` for the current agent.
        """
        return self.rank(good1) < self.rank(good2)

    @staticmethod
    @FileCache()
    def _is_ordinally_less(agent, alloc1, alloc2):
        """
        Checks if :param:`alloc1` is ordinally less than :param:`alloc2` for agent :param:`agent`
        :param agent:
        :param alloc1: An allocation
        :param alloc2: An allocation
        :return: True if :param:`alloc1` is ordinally less :param:`alloc2`for agent :param:`agent`
        """
        injections = Utils.get_possible_injections(alloc1, alloc2)
        ordinally_less = False
        for injection in injections:
            ordinally_less = True
            for (x, y) in injection:
                if not agent.compare_goods(y, x):
                    ordinally_less = False
                    break
            if ordinally_less:
                break
        return ordinally_less

    def is_ordinally_less(self, alloc1, alloc2=None):
        """
        Checks if :param:`alloc1` is ordinally less than :param:`alloc2`.
        :param alloc1: An allocation
        :param alloc2: An allocation, If set to None, the allocation :param:`alloc1` is compared to
                        its complementary in the set of goods.
        :return: True if :param:`alloc1` is ordinally less :param:`alloc2`
        """
        if alloc2 is None:
            alloc2 = tuple([good for good in self.preferences if good not in alloc1])
        if not isinstance(alloc1, tuple):
            alloc1 = tuple(alloc1)
        return Agent._is_ordinally_less(self, alloc1, alloc2)

    def borda(self, goods, N=None):
        """
        Return the Borda score of this agent.
        :param goods: goods allocated to agent
        :param N: number of goods. If None, set to `len(goods) * 2`
        :return: Borda score of the current allocation
        """
        _sum = 0
        if N is None:
            N = len(goods) * 2

        for good in goods:
            _sum += N + 1 - self.rank(good)

        return _sum


class Allocation(object):
    """
    Represents an allocation of goods for two agents
    """
    def __init__(self, agent1, goods1, agent2, goods2):
        """
        :param agent1:
        :type agent1: Agent
        :param goods1:
        :type goods1: collections.Iterable
        :param agent2:
        :type agent2: Agent
        :param goods2: collections.Iterable
        """
        self.a1 = agent1
        self.g1 = tuple(sorted(goods1))
        self.a2 = agent2
        self.g2 = tuple(sorted(goods2))

    def __eq__(self, other):
        """
        An agent is equal to another one if they concern the same agents and give the same goods for the agents
        :param other:
        :return:
        """
        if not isinstance(other, Allocation):
            return False
        else:
            return other.a1 == self.a1 and other.a2 == self.a2 and other.g1 == self.g1 and other.g2 == self.g2

    def __hash__(self):
        return (self.a1, self.g1, self.a2, self.g2).__hash__()

    def __repr__(self):
        return {self.a1: self.g1, self.a2: self.g2}.__repr__()

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, item):
        if item == 0:
            return self.g1
        if item == 1:
            return self.g2
        return None

    def __iter__(self):
        yield from [self.g1, self.g2]

    @staticmethod
    @MemoryCache(cache_size=10)
    def generate_all_allocations(agents, goods):
        '''
        :param agents: the two agents
        :type agents: list|tuple
        :param goods: the goods
        :type goods: Sized
        :return: A set of all the possible allocations
        '''
        return set([Allocation(agents[0], g1, agents[1], [good for good in goods if good not in g1])
                    for g1 in itertools.combinations(goods, len(goods)//2)])

    @staticmethod
    def get_allocations(agents, allocations):
        """
        Retrieves a set of Allocation objects from allocations represented by iterables
        :param agents: The agents
        :type agents: list|tuple
        :param allocations: The allocations represented by iterables like [(0, 1), (2, 3)]
        :type allocations: collections.Iterable
        :return: A set of Allocation objects
        """
        result = set()
        for allocation in allocations:
            result.add(Allocation(agents[0], allocation[0], agents[1], allocation[1]))
        return result


class Problem(object):
    """
    This class represents fair division problems with indivisible items and agents with ordinal preferences over them
    """
    def __hash__(self):
        return tuple((self.agents, self.goods)).__hash__()

    def __eq__(self, other):
        if isinstance(other, Problem):
            return other.agents == self.agents and other.goods == self.goods
        return False

    def __init__(self, agents, goods):
        """
        Initializes a problem
        :param agents: The agents of the problem
        :type agents: collections.Iterable
        :param goods: The goods of the problem
        :type goods: collections.Iterable
        """
        self.agents = tuple(agents)
        self.goods = tuple(goods)

    def max_min_rank(self):
        """
        :return: Computes the max_min_rank of the problem as defined in the article
        """
        k = 0
        for good in self.goods:
            best_rank = len(self.goods)
            for agent in self.agents:
                rank = agent.rank(good)
                if rank <= best_rank:
                    best_rank = rank
            if k <= best_rank:
                k = best_rank
        return k

    @staticmethod
    @FileCache()
    def generate_possible_problems(problems_size=2):
        """
        :param problems_size: The size of the desired problems (should an even number)
        :type problems_size: int
        :return: All the possible problems of the given size
        """
        problems = list()
        goods = [Good(str(i)) for i in range(problems_size)]
        for preferences_b in itertools.permutations(goods):
            a = Agent("A", goods[:])
            b = Agent("B", list(preferences_b))
            problem = Problem((a, b), goods)
            problems.append(problem)
        return problems