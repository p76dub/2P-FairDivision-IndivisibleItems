# -*- coding: utf-8 -*-
from fairdiv import Allocation
from funcache import FileCache, MemoryCache
from multiprocessing import Pool, cpu_count
import time


class Statistics(object):

    A_KEY = "Allocation"

    def __init__(self, allocs, agents, functions):
        """
        Create a new object Statistics, storing allocations for all agents in `agents`.

        :param allocs: All possible allocations, **NOT** the ones to store
        :param agents: Agents
        :param functions: a dict key -> function that will be applied to new allocations (see
        :meth:`add`). Functions must take these arguments : alloc, all_allocs, agents. Use lambda if
        some parameters aren't used.
        """
        self.allocs = allocs
        self.agents = agents
        self.functions = functions
        self._data = []

    @property
    def data(self):
        return self._data[:]

    def add(self, alloc):
        """
        Add a new allocation to the ones stored. All functions will be applied and result will be
        stored as a dict, keys being the same as the ones provided in the constructor.

        :param alloc: the allocation to add
        """
        result = {
            self.A_KEY: alloc
        }
        for k, v in self.functions.items():
            result[k] = v(alloc, self.allocs, self.agents)
        self._data.append(result)

    def formatted_text(self):
        """
        Get a string formatted to print results

        :return: a formatted string
        :rtype: str
        """
        result = "Allocations:\n"
        for data in self._data:
            result += "\t{}: {}\n".format(self.A_KEY, data[self.A_KEY])
            result += "".join(
                ["\t\t{}: {}\n".format(k, v) for k, v in data.items() if k != self.A_KEY]
            )
        return result

    def __str__(self):
        return self._data.__str__()

    def __repr__(self):
        return self.formatted_text()
