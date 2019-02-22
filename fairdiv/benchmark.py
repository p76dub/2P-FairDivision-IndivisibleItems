from multiprocessing import Pool, cpu_count
from funcache import FileCache, MemoryCache
from fairdiv import properties, algorithm
from fairdiv import Problem
from fairdiv import Allocation


class Benchmark(object):
    """
    This class provides Benchmarking utilities for the Properties & Algorithms of fair division problems.
    It uses multiprocessing as possible to speed up calculations.
    Also to speed up calculations, the results of the methods of this class are cached in files
    """
    _pool = None
    _pool_size = 0

    _algorithms = {
        "bottom up": algorithm.BottomUp,
        "trump": algorithm.Trump,
        "original sequential": algorithm.OriginalSequential,
        "restricted sequential": algorithm.RestrictedSequential,
        "singles doubles": algorithm.SinglesDoubles
    }
    _properties = {
        "ordinal envy freeness": properties.OrdinalEnvyFreeness,
        "borda egalitarian": properties.BordaEgalitarian,
        "borda envy freeness": properties.BordaEnvyFreeness,
        "borda max min": properties.BordaMaxMin,
        "borda nash": properties.BordaNash,
        "borda pareto": properties.BordaPareto,
        "envy freeness": properties.EnvyFreeness,
        "maximal borda sum": properties.MaximalBordaSum,
        "max min": properties.MaxMin,
        "ordinal pareto": properties.OrdinalPareto,
    }

    @staticmethod
    def init_pool():
        """
        Initializes the Pool of processes
        :return:
        """
        if Benchmark._pool is not None:
            return
        Benchmark._pool_size = cpu_count()
        if Benchmark._pool_size > 1:
            Benchmark._pool_size -= 1
        Benchmark._pool = Pool(Benchmark._pool_size)

    @staticmethod
    def benchmark_problem(problem: Problem):
        """
        Benchmarks all the algorithms on a given problem.
        No multiprocessing is used in this method because it is assumed that it was already called by multiprocessing
        :param problem: The problem to benchmark the algorithms on
        :return: A dictionary of the form algorithm_key -> results
        """
        result = {key: algo.compute(problem) for key,algo in Benchmark._algorithms.items()}
        return result

    @staticmethod
    def benchmark_property(t):
        """
        Benchmarks a given property on a given problem
        No multiprocessing is used in this method because it is assumed that it was already called by multiprocessing
        :param t: A tuple of the form (property_to_check, problem_, allocations) Where allocations is a collection of all possible allocations of the problem
        :return: A set of allocation that verifies the property
        """
        to_check,problem, allocations = t
        result = set()
        if to_check not in Benchmark._properties:
            return result
        for allocation in allocations:
            if Benchmark._properties[to_check].check(allocation, problem.agents, allocations):
                result.add(allocation)
        return result

    @staticmethod
    @FileCache()
    def benchmark_size(problems_size):
        """
        This method benchmarks all the algorithms & all the properties on all problems of a given size.
        :param problems_size: The size of problems (the number of goods) to consider.
        :return: A dictionary of the form
        problem -> {"algorithms" -> {algorithm -> allocations}, "properties" -> {property -> allocation}}
        """
        assert problems_size > 0
        assert problems_size % 2 == 0

        Benchmark.init_pool()
        FileCache.enable_multiprocessing(Benchmark._pool, Benchmark._pool_size)
        MemoryCache.enable_multiprocessing(Benchmark._pool, Benchmark._pool_size)
        result = dict()
        problems = Problem.generate_possible_problems(problems_size)
        result["problems"] = dict()
        problems_solutions = Benchmark._pool.map(Benchmark.benchmark_problem, problems)
        allocations = None
        properties = list(Benchmark._properties.keys())
        for i in range(len(problems)):
            result["problems"][problems[i]] = dict()
            result["problems"][problems[i]]["algorithms"] = problems_solutions[i]
            if allocations is None:
                allocations = Allocation.generate_all_allocations(problems[i].agents, problems[i].goods)
            properties_results = Benchmark._pool.map(Benchmark.benchmark_property, [(prop, problems[i], allocations) for prop in properties])
            result["problems"][problems[i]]["properties"] = dict()
            for j in range(len(properties)):
                result["problems"][problems[i]]["properties"][properties[j]] = properties_results[j]
        return result


if __name__ == "__main__":
    result = Benchmark.benchmark_size(6)
    FileCache.save_files()
