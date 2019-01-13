# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import properties as prop


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
