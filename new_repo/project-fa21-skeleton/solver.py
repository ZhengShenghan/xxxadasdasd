from parse import read_input_file, write_output_file
import math
import os
import random
import dynamic
from threading import Thread
from multiprocessing.pool import ThreadPool
import FuncSets
import FuncSets_BFS
import Task
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


def bench_mark(tasks, eval):
    profit_margin = EVAL_FUNCTIONS[eval]
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

    # review_and_revise(sequence, profit, tasks)
    f_sequence = [task.get_task_id() for task in sequence]
    assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
    return f_sequence, profit


def review_and_revise(curr_sequence, curr_profit, rem_tasks):
    time = 0
    for i in range(len(curr_sequence)):
        curr_task = curr_sequence[i]
        curr_task_overtime = time + curr_task.get_duration() - curr_task.get_deadline()
        curr_task_profit = curr_task.get_late_benefit(curr_task_overtime)
        for t in rem_tasks:
            t_overtime = time + t.get_duration() - t.get_deadline()
            t_profit = t.get_late_benefit(t_overtime)
            if curr_task_profit < t_profit:
                copy_seq = curr_sequence.copy()
                copy_seq[i] = t
                if curr_profit < determine_profit(copy_seq):
                    curr_sequence[i] = t


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

# def check_outputs():
#     for test_type in os.listdir('outputs/'):
#         if test_type[0] != '.':
#             for out_path in os.listdir('outputs/' + test_type):
#                 if out_path[0] != '.':
#                     output_path = 'outputs/' + test_type + '/' + out_path[:-3] + '.out'
#                     with open(out_path, encoding="utf-8-sig") as out_file:
#                         while out_file
#

# Here's an example of how to run your solver.
if __name__ == '__main__':
    count = 0
    bp1 = 0
    bp2 = 0
    bp3 = 0
    net = 0
    # task0 = Task.Task(0, 936, 432, 10)
    # task1 = Task.Task(1, 1440, 576, 20)
    # task2 = Task.Task(2, 1152, 216, 5)
    # task3 = Task.Task(3, 432, 288, 30)
    # task4 = Task.Task(4, 576, 360, 15)
    # tasks = [task0, task1, task2, task3, task4]
    # print(dynamic.dp_solver(tasks))
    pool = ThreadPool(processes=16)
    for test_type in os.listdir('inputs/'):
        if test_type[0] != '.':
            for input_path in os.listdir('inputs/' + test_type):
                if input_path[0] != '.':
                    output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
                    input_path = 'inputs/' + test_type + '/' + input_path
                    tasks = read_input_file(input_path)

                    # async_result = pool.apply_async(dynamic.dp_solver, (tasks,))  # tuple of args for foo
                    #
                    # # do some other stuff in the main process
                    # return_val = async_result.get()  # get the return value from your function.
                    # net += return_val[0]
                    # write_output_file(output_path, return_val[1])


                    # tasks1 = tasks.copy()
                    # tasks2 = tasks.copy()
                    # tasks3 = tasks.copy()
                    # out1 = 0, 0
                    # out2 = 0, 0
                    # out3 = 0, 0
                    # out4 = 0, 0
                    p, s = dynamic.dp_solver(tasks)
                    net += p
                    write_output_file(output_path, s)
                    # out1 = bench_mark(tasks1, 'adv_profit_ratio')
                    # branch_bound = FuncSets_simulated_annealing.branch_and_bound(tasks)
                    # out2 = branch_bound.return_sequence(), branch_bound.result()
                    # out3 = naive_simulated_annealing(tasks3, 2000)


                    # sequence, profit = max([out1, out2, out3], key=lambda x: x[1])
                    # net += profit
                    # write_output_file(output_path, sequence)
                    #
                    # bp1 += out1[1]
                    # bp2 += out2[1]
                    # bp3 += out3[1]
                    count += 1
    print(f'Net: {net/count}')
    # print(f'Benchmark1 Avg: {bp1/count}\nSimulated Annealing Avg: {bp2/count}\nNaive Simulated Annealing Avg: {bp3/count}\nNet: {net/count}')

# if __name__ == '__main__':
#     total = 0
#     count = 0
#     for test_type in os.listdir('inputs/'):
#         if test_type[0] != '.':
#             for input_path in os.listdir('inputs/' + test_type):
#                 if input_path[0] != '.':
#                     output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
#                     input_path = 'inputs/' + test_type + '/' + input_path
#                     tasks = read_input_file(input_path)
#                     branch_and_bound = FuncSets_simulated_annealing.branch_and_bound(tasks)
#                     total += branch_and_bound.result()
#                     count += 1
#                     # print(branch_and_bound.result())
#                     # if count % 200:
#                     #     print(total/count)
#                     # print('\n')
#     print(f'Average profit: {total/count}')
# =======
#     sum = 0
#     num = 0
#     for test_type in os.listdir('inputs/'):
#             if test_type[0] != '.':
#                 for input_path in os.listdir('inputs/' + test_type):
#                     if input_path[0] != '.':
#                         output_path = 'outputs/' + test_type + '/' + input_path[:-3] + '.out'
#                         input_path = 'inputs/' + test_type + '/' + input_path
#                         tasks = read_input_file(input_path)
#                         branch_and_bound = FuncSets_simulated_annealing.branch_and_bound(tasks)
#                         t = branch_and_bound.result()
#                         sum += t
#                         branch_and_bound.show()
#                         print(t)
#                         num += 1
#                         print('\n')
#     print("---")
#     print(sum/num)
# >>>>>>> a3c8ca6ac7e483f7163815d70b843dde17b8c77d
