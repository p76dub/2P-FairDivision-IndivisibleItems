# -*- coding: utf-8 -*-
import collections
import itertools
import pickle
import atexit
import algorithm
from functools import total_ordering


class Database(object):
    """
    This class provides caches for functions.
    Instead of re-computing the result of a function, just store it in one of the caches & retrieve it later.
    The two provided caches are memory cache & file cache.
    Basically the later is persistent across executions while the former is not.
    """
    _db_files_root = "resources/database/"
    _db_files_extension = ".db"
    _open_files = dict()
    _mem_cache = dict()
    _mem_cache_sizes = dict()
    _mem_cache_accesses = dict()
    _is_at_exit_set = False

    @staticmethod
    def get_from_file(func, *args):
        """
        This method implements the file cache.
        Checks if a function's result for the given arguments is already present in the cache. If so, it's returned.
        If the result is not already in the cache, it's computed & added to it.
        :param func: The function whose result is desired
        :param args: The arguments to pass to the function.
        :return: The result of applying the function to the given arguments
        """
        # Check if the file is already loaded
        if func.__qualname__ not in Database._open_files:
            # If not, we try to load it.

            # We make sure that the file will be re-written into disk when the program finishes
            if not Database._is_at_exit_set:
                atexit.register(Database.save_files)
                Database._is_at_exit_set = True
            try:
                with open(Database.get_file_path(func), "rb") as f:
                    Database._open_files[func.__qualname__] = pickle.load(f)
            except FileNotFoundError:
                # If the file doesn't exist, we initialize an empty dictionary for it
                Database._open_files[func.__qualname__] = dict()

        func_dict = Database._open_files[func.__qualname__]

        # We retrieve the key for the args in the function dictionary
        args_key = Database.get_args_key(args)
        if args_key not in func_dict:
            # If the functions's result with the given params wasn't already computed
            temp = func(*args)
            if isinstance(temp, collections.Iterable):
                temp = list(temp)
            func_dict[args_key] = temp
        # Return the result
        return func_dict[args_key]

    @staticmethod
    def save_files():
        """
        Saves the files that are loaded in memory (& so may have changed) into disk
        """
        for func in Database._open_files:
            with open(Database.get_file_path(func), "wb") as f:
                pickle.dump(Database._open_files[func], f)
                f.close()

    @staticmethod
    def get_mem(func, *args, cache_size=1000):
        """
        This method implements the memory cache
        Checks if a function's result for the given arguments is already present in the cache. If so, it's returned.
        If the result is not already in the cache, it's computed & added to it.
        :param func: The function whose result is desired
        :param args: The arguments to pass to the function
        :param cache_size: The size of the cache. ie, the maximum number of results to store.
        :return: The result of applying the function to the given arguments
        """
        if func.__qualname__ not in Database._mem_cache:
            Database._mem_cache[func.__qualname__] = dict()
            Database._mem_cache_accesses[func.__qualname__] = []
        Database._mem_cache_sizes[func.__qualname__] = cache_size
        args_key = Database.get_args_key(args)
        if args_key not in Database._mem_cache[func.__qualname__]:
            temp = func(*args)
            if isinstance(temp, collections.Iterable):
                temp = list(temp)
            Database._mem_cache[func.__qualname__][args_key] = temp
            if len(Database._mem_cache[func.__qualname__]) > Database._mem_cache_sizes[func.__qualname__]:
                del(Database._mem_cache[func.__qualname__][Database._mem_cache_accesses[func.__qualname__].pop(0)])
            if args_key in Database._mem_cache_accesses[func.__qualname__]:
                Database._mem_cache_accesses[func.__qualname__].remove(args_key)
            Database._mem_cache_accesses[func.__qualname__].append(args_key)
        return Database._mem_cache[func.__qualname__][args_key]

    @staticmethod
    def get_file_path(func):
        """
        :param func: A function object or its qualname
        :return: Retrieves the file path of the cache of a function
        """
        if not isinstance(func, str):
            func = func.__qualname__
        return Database._db_files_root + func + Database._db_files_extension

    @staticmethod
    def get_args_key(args):
        """
        :param args: an object representing the arguments to be passed to a function
        :return:
        """
        # Since lists are not hashable,
        # We make sure to convert them to tuples, (& also their contents)
        if isinstance(args, collections.Iterable):
            args = tuple([Database.get_args_key(arg) for arg in args])
        return args


def cache(func):
    """
    This function wraps another one with the file cache.
    It can be used as a decorator so there won't be any need to call it explicitly.
    :param func: The function to wrap
    :return: The given function wrapped with the file cache
    """
    def inner(*args):
        return Database.get_from_file(func, *args)
    return inner


class mem_cache(object):
    """
    This class is meant to be used as a decorator to make a function's result be stored in a cache in the memory.
    """
    def __init__(self,cache_size):
        """
        Builds the function wrapper with a given cache size.
        :param cache_size: The cache size
        """
        self.cache_size = cache_size

    def __call__(self, original_func):
        """
        :param original_func: The function to wrap
        :return: the wrapped function that passes by the cache
        """
        decorator_self = self

        def wrappee(*args):
            return Database.get_mem(original_func, *args, cache_size=decorator_self.cache_size)
        return wrappee


class Utils(object):
    """
    Groups some utility methods
    """

    @staticmethod
    @mem_cache(cache_size=1000)
    def get_possible_injections(alloc1, alloc2):
        """
        Returns a list of possible mappings from alloc1 to alloc2.
        Note that this method's results are stored in the memory cache.
        :param alloc1:
        :param alloc2:
        :return:
        """
        return [[j for j in map(lambda x, y: (x, y), alloc1, i)] for i in itertools.permutations(alloc2)]

    @staticmethod
    @cache
    def generate_possible_problems(problems_size=2, envy_free_only=False):
        problems = []
        goods = [Good(str(i)) for i in range(problems_size)]
        for preferences_b in itertools.permutations(goods):
            a = Agent("A", goods[:])
            b = Agent("B", list(preferences_b))
            problem = ((a, b), goods)
            if envy_free_only:
                if len(algorithm.trump_algorithm(*problem)) == 0:
                    continue
            problems.append(problem)
        return problems

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
    @cache
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

    @staticmethod
    @mem_cache(cache_size=10)
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


def max_min_rank(agents, goods):
    """
    :param agents: The agents
    :param goods: The goods
    :return: Computes the max_min_rank of a problem as defined in the article
    """
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
