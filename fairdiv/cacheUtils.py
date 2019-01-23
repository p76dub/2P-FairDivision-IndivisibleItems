import pickle
import atexit
import collections


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
            try:
                f = open(Database.get_file_path(func), "rb+")
                changed = pickle.load(f)
                if changed is not None and isinstance(changed, dict):
                    for key in changed:
                        if key not in Database._open_files[func]:
                            Database._open_files[func][key] = changed[key]
            except FileNotFoundError:
                f = open(Database.get_file_path(func), "wb")
            pickle.dump(Database._open_files[func], f)
            f.close()
        Database._open_files.clear()

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