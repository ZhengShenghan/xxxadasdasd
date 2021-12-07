from parse import read_input_file, write_output_file
import math
import os
import random
import dynamic
import sys
import FuncSets_simulated_annealing
sys.setrecursionlimit(20000)

EVAL_FUNCTIONS = {
    'adv_profit_ratio': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration(),
    'profit_ratio': lambda task: task.get_max_benefit() / task.get_duration(),
    'deadline': lambda task: task.get_deadline(),
    'deadline_profit': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_deadline(),
    'linear': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration() + (task.get_max_benefit() / task.get_deadline()),
}


def naive_simulated_annealing(tasks, temp):
    profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = EVAL_FUNCTIONS['deadline_profit']
    time = 0
    profit = 0.0
    buffer_tasks = tasks.copy()
    sequence = []
    while len(tasks) > 0:
        selection = sorted(buffer_tasks, key=deadline(time), reverse=True)[:10]

        if not selection:
            break
        # Sort by the profit/duration
        choice = sorted(selection, key=profit_margin(time), reverse=True)[0]

        # Random choice out of possible options
        random_choice = selection[random.randint(0, len(selection) - 1)]

        # Determine if the time has gone over the deadline
        overtime = time + choice.get_duration() - choice.get_deadline()

        # temp schedule
        t = temp / (time + 1)

        # Difference in energy
        diff = choice.get_late_benefit(overtime) - random_choice.get_late_benefit(overtime)

        # Annealing constant
        anneal = math.exp(-diff / t)
        if diff >= 0 and random.random() < anneal:
            choice = random_choice

        if time + choice.get_duration() > 1440:
            time -= choice.get_duration()
            break

        # Add the duration of the task to the time
        time += choice.get_duration()

        # Remove task from tasks
        buffer_tasks.remove(choice)

        # Add the task to the sequence
        sequence.append(choice)

        if overtime > 0:
            swap(sequence, choice)
            new_profit = determine_profit(sequence)
            if profit + choice.get_late_benefit(overtime) < new_profit:
                profit = new_profit
        else:
            # Add expected profit from igloo
            profit += choice.get_late_benefit(overtime)

    f_sequence = [task.get_task_id() for task in sequence]
    assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
    return f_sequence, profit


def bench_mark(tasks):
    profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = EVAL_FUNCTIONS['deadline_profit']
    sequence = []
    slip = 10
    time = 0
    profit = 0.0

    while len(tasks) > 0:
        selected = sorted(tasks, key=deadline(time), reverse=True)[:10]

        # Sort by the profit/duration
        choice = sorted(selected, key=profit_margin(time), reverse=True)[0]

        # Remove task from tasks
        tasks.remove(choice)

        # Slip if our choice of task with put us over the deadline.
        # If we are out of slips break from the algorithm.
        if time + choice.get_duration() > 1440:
            if not slip:
                break
            slip -= 1
        else:
            # Add the duration of the task to the time
            time += choice.get_duration()

            # Determine if the time has gone over the deadline
            overtime = time - choice.get_deadline()

            # Add the task to the sequence
            sequence.append(choice)

            if overtime > 0:
                swap(sequence, choice)
                new_profit = determine_profit(sequence)
                if profit + choice.get_late_benefit(overtime) < new_profit:
                    profit = new_profit
            else:
                # Add expected profit from igloo
                profit += choice.get_late_benefit(overtime)

    f_sequence = [task.get_task_id() for task in sequence]
    assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
    return f_sequence, profit


def swap(sequence, curr_task):
    best = -1
    for i in range(len(sequence)-1):
        task = sequence[i]
        if sequence[best].get_deadline() < task.get_deadline():
            best = i

    temp = sequence[best]
    sequence[best] = curr_task
    sequence[-1] = temp


def determine_profit(sequence):
    time = 0
    profit = 0.0
    for task in sequence:
        time += task.get_duration()
        overtime = time - task.get_deadline()
        profit += task.get_late_benefit(overtime)
    return profit


def run_mult_alg(tasks):
    tasks1 = tasks.copy()
    tasks2 = tasks.copy()
    tasks3 = tasks.copy()
    out1 = 0, 0
    out2 = 0, 0
    out3 = 0, 0
    branch_bound = FuncSets_simulated_annealing.branch_and_bound(tasks2)

    # Simply greedy
    out1 = bench_mark(tasks1)

    # Branch and bound
    out2 = branch_bound.return_sequence(), branch_bound.result()

    # Simulated Annealing
    out3 = naive_simulated_annealing(tasks3, 2000)

    sequence, profit = max([out1, out2, out3], key=lambda x: x[1])
    write_output_file(output_path, sequence)
    return profit


# Here's an example of how to run your solver.
if __name__ == '__main__':
    count = 0
    bp1 = 0
    bp2 = 0
    bp3 = 0
    net = 0
    for test_type in os.listdir('inputs/'):
        if test_type[0] != '.':
            for input_path in os.listdir('inputs/' + test_type):
                if input_path[0] != '.':
                    output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
                    input_path = 'inputs/' + test_type + '/' + input_path
                    tasks = read_input_file(input_path)

                    p, s = dynamic.dp_solver(tasks)
                    net += p
                    write_output_file(output_path, s)

                    # Uncomment to run the three algorithm stack
                    # net += run_mult_alg(tasks)

                    count += 1
    print(f'Net: {net/count}')
