from fairdiv import *
import time
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, cpu_count

if __name__ == "__main__":
    use_pool = False
    process = False
    if use_pool:
        if process:
            pool = Pool(cpu_count())
        else:
            pool = ThreadPool(cpu_count())
    for j in range(6):
        number_of_goods = (j+1) * 2

        print("testing with " + str(number_of_goods))
        goods = [Good(str(i)) for i in range(number_of_goods)]

        a1 = Agent("agent1", goods[:])
        a2 = Agent("agent2", goods[::-1])

        start_time = time.time()

        allocs = Allocation.generate_all_allocations((a1, a2), goods)

        if number_of_goods == 14:
            old_allocs = allocs
            allocs = []
            i=0
            for alloc in old_allocs:
                allocs.append(alloc)
                i += 1
                if i == 100000:
                    break

        if use_pool:
            pool.map(a1.is_ordinally_less, [alloc[0] for alloc in allocs])
            pool.map(a2.is_ordinally_less, [alloc[1] for alloc in allocs])
        else:
            for alloc in allocs:
                a1.is_ordinally_less(alloc[0])
                a2.is_ordinally_less(alloc[1])

        elapsed_time = time.time() - start_time
        print(elapsed_time)
