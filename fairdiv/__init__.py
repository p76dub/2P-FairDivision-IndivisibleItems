# -*- coding: utf-8 -*-
import collections
import itertools
import pickle
import atexit


class Database(object):
    _db_files_root = "resources/database/"
    _db_files_extension = ".db"
    _open_files = dict()
    _is_at_exit_set = False

    @staticmethod
    def get(func, *params):
        if func.__qualname__ not in Database._open_files:
            if not Database._is_at_exit_set:
                atexit.register(Database.save_files)
                Database._is_at_exit_set = True
            file_path = Database._db_files_root + func.__qualname__ + Database._db_files_extension
            try:
                Database._open_files[func.__qualname__] = pickle.load(open(file_path, "rb"))
            except FileNotFoundError:
                Database._open_files[func.__qualname__] = dict()
        func_dict = Database._open_files[func.__qualname__]
        if params not in func_dict:
            temp = func(*params)
            if isinstance(temp, collections.Iterable):
                temp = list(temp)
            func_dict[params] = temp
        return func_dict[params]

    @staticmethod
    def save_files():
        for func in Database._open_files:
            file_path = Database._db_files_root + func + Database._db_files_extension
            pickle.dump(Database._open_files[func], open(file_path, "wb"))


def cache(func):
    def inner(*args):
        return Database.get(func, *args)
    return inner


class Utils(object):

    @staticmethod
    def get_possible_injections(alloc1, alloc2):
        """
        Returns a list of possible mappings from alloc1 to alloc2
        :param alloc1:
        :param alloc2:
        :return:
        """
        return [[j for j in map(lambda x, y: (x, y), alloc1, i)] for i in itertools.permutations(alloc2)]


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

    def compare_goods(self, good1, good2):
        return self.rank(good1) < self.rank(good2)

    @staticmethod
    @cache
    def _is_ordinally_less(agent, alloc1, alloc2=None):
        injections = Utils.get_possible_injections(alloc1, alloc2)
        ordinally_less = False
        for injection in injections:
            ordinally_less = True
            for (x,y) in injection:
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
        :param alloc2: An allocation, If set to None, the allocation :param:`alloc1` is compared to its complementary in the set of goods.
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

    @staticmethod
    def generate_all_allocations(goods):
        """
        Generate all possible allocations. I think it should generate all different permutations
        :param goods: all considered goods
        :return: allocation for 2 agents
        """
        allocs = list(itertools.combinations(goods, len(goods) // 2))
        return [(tuple(alloc), tuple([g for g in goods if g not in alloc])) for alloc in allocs]


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
