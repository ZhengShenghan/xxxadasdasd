from parse import read_input_file, write_output_file
import math
import os
import FuncSets
import FuncSets_BFS
import sys
import FuncSets_simulated_annealing
sys.setrecursionlimit(20000)

if __name__ == '__main__':
    sum = 0
    num = 0
    for test_type in os.listdir('inputs/'):
            if test_type[0] != '.':
                for input_path in os.listdir('inputs/' + test_type):
                    if input_path[0] != '.':
                        output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
                        input_path = 'inputs/' + test_type + '/' + input_path
                        tasks = read_input_file(input_path)
                        branch_and_bound = FuncSets_simulated_annealing.branch_and_bound(tasks)
                        t = branch_and_bound.result()
                        sum += t
                        branch_and_bound.show()
                        print(t)
                        num += 1
                        print('\n')
    print("---")
    print(sum/num)