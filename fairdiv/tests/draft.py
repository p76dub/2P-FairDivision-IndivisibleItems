import itertools
from fairdiv import *
import time
import sys
import algorithm


for i in Allocation.generate_all_allocations((Agent("a"), (Agent("b"))), [Good(str(i)) for i in range(4)]):
    print(i)


"""
start_time = time.time()
itertools.permutations(range(10))
first_time = time.time() - start_time
start_time = time.time()
itertools.permutations(range(10))
second_time = time.time() - start_time

print(first_time)
print(second_time)
print(str(first_time / second_time))



start_time = time.time()
Utils.get_possible_injections(range(10), range(10))
first_time = time.time() - start_time
start_time = time.time()
Utils.get_possible_injections(range(10), range(10))
second_time = time.time() - start_time

print(first_time)
print(second_time)
print(str(first_time / second_time))
"""

"""


good = Good("1")
for i in itertools.permutations([good]):
    print(i)

for i in itertools.permutations(([good])):
    print(i)
"""