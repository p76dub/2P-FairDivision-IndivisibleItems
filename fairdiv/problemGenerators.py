from cacheUtils import cache
from fairdiv import Good, Agent, Utils
from algorithm import trump_algorithm
import itertools


@cache
def generate_possible_problems(problems_size=2, envy_free_only=False):
    problems = list()
    goods = [Good(str(i)) for i in range(problems_size)]
    if not envy_free_only:
        for preferences_b in itertools.permutations(goods):
            a = Agent("A", goods[:])
            b = Agent("B", list(preferences_b))
            problem = ((a, b), goods)
            problems.append(problem)
    else:
        all_problems = generate_possible_problems(problems_size)
        for problem in all_problems:
            if len(trump_algorithm(*problem)) == 0:
                continue
            problems.append(problem)
    return problems