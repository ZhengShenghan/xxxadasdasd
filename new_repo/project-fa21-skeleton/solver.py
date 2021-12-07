from parse import read_input_file, write_output_file
import math
import os
import FuncSets
import FuncSets_BFS
import sys
import FuncSets_simulated_annealing
sys.setrecursionlimit(20000)

if __name__ == '__main__':
    total = 0
    count = 0
    for test_type in os.listdir('inputs/'):
        if test_type[0] != '.':
            for input_path in os.listdir('inputs/' + test_type):
                if input_path[0] != '.':
                    output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
                    input_path = 'inputs/' + test_type + '/' + input_path
                    tasks = read_input_file(input_path)
                    branch_and_bound = FuncSets_simulated_annealing.branch_and_bound(tasks)
                    total += branch_and_bound.result()
                    count += 1
                    # print(branch_and_bound.result())
                    # if count % 200:
                    #     print(total/count)
                    # print('\n')
    print(f'Average profit: {total/count}')
