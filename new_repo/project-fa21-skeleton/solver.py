from parse import read_input_file, write_output_file
import os
import sys
from dynamic import dp_solver
from greedy import basic_greedy, basic_simulated_annealing
import FuncSets_simulated_annealing
sys.setrecursionlimit(20000)

EVAL_FUNCTIONS = {
    'adv_profit_ratio': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration(),
    'profit_ratio': lambda task: task.get_max_benefit() / task.get_duration(),
    'deadline': lambda task: task.get_deadline(),
    'deadline_profit': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_deadline(),
    'linear': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration() + (task.get_max_benefit() / task.get_deadline()),
}


def run_mult_alg(tasks):
    # Make copies of tasks so that we don't mutate tasks
    tasks1 = tasks.copy()
    tasks2 = tasks.copy()
    tasks3 = tasks.copy()

    branch_bound = FuncSets_simulated_annealing.branch_and_bound(tasks2)

    # Simply greedy
    out1 = basic_greedy(tasks1)

    # Branch and bound
    out2 = branch_bound.return_sequence(), branch_bound.result()

    # Simulated Annealing
    out3 = basic_simulated_annealing(tasks3, 2000)

    sequence, profit = max([out1, out2, out3], key=lambda x: x[1])
    write_output_file(output_path, sequence)
    return profit


# Here's an example of how to run your solver.
if __name__ == '__main__':
    for test_type in os.listdir('inputs/'):
        if test_type[0] != '.':
            for input_path in os.listdir('inputs/' + test_type):
                if input_path[0] != '.':
                    output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
                    input_path = 'inputs/' + test_type + '/' + input_path
                    tasks = read_input_file(input_path)

                    _, s = dp_solver(tasks)
                    write_output_file(output_path, s)

                    # Uncomment to run the three algorithm stack
                    # run_mult_alg(tasks)

