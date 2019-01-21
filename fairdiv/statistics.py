# -*- coding: utf-8 -*-
import properties as prop


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



def gather_data(agents, allocs, all_allocs, pareto=True, max_min=True, envy=True):
    # Eliminate duplicates
    uniques = []
    for a in allocs:
        if a not in uniques:
            uniques.append(a)

    allocs = uniques

    # Create structure
    stats = {
        "Allocations found": len(allocs),
        "Explored space": len(allocs) / len(all_allocs),
        "Allocations": []
    }

    # Iterate over allocations and create stats about them
    for alloc in allocs:
        a_stats = {
            agents[i]: v for i, v in enumerate(alloc)
        }

        if pareto:
            a_stats["Is pareto"] = prop.is_pareto(alloc, all_allocs, agents)

        if max_min:
            a_stats["Is max-min"] = prop.is_max_min(alloc, all_allocs, agents)

        if envy:
            a_stats["Is envy-free"] = prop.is_envy_free(alloc, agents)

        stats["Allocations"].append({"Allocation": a_stats})

    return stats


def print_statistics(stats):

    def print_one(s):
        print("Allocations found: {}".format(s["Allocations found"]))
        print("Explored space: {}".format(s["Explored space"]))
        print("Allocations :")
        for alloc in s["Allocations"]:
            for k, v in alloc.items():
                print("\t{}: {}".format(k, v))

    if type(stats) == list:
        for e in stats:
            print_one(e)
    else:
        print_one(stats)
