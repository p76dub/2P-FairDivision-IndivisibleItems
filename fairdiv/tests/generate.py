from fairdiv import *

if __name__ == "__main__":
    for j in range(10):
        number_of_goods = (j+1) * 2

        print("testing with " + str(number_of_goods))
        goods = [Good(str(i)) for i in range(number_of_goods)]

        a1 = Agent("agent1", goods[:])
        a2 = Agent("agent2", goods[::-1])

        allocs = Good.generate_all_allocations(goods)
        for alloc in allocs:
            a1.is_ordinally_less(alloc[0])
            a2.is_ordinally_less(alloc[1])

