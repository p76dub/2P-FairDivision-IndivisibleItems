from cacheUtils import cache
from fairdiv import Good, Agent
from algorithm import trump_algorithm
import itertools


@cache
def generate_possible_problems(problems_size=2):
    """
    :param problems_size: The size of the desired problems (should an even number)
    :return: All the possible problems of the given size
    """
    problems = list()
    goods = [Good(str(i)) for i in range(problems_size)]
    for preferences_b in itertools.permutations(goods):
        a = Agent("A", goods[:])
        b = Agent("B", list(preferences_b))
        problem = ((a, b), goods)
        problems.append(problem)
    return problems
