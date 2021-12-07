from parse import read_input_file, write_output_file
import math
import random
import os



EVAL_FUNCTIONS = {
    'adv_profit_ratio': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration(),
    'profit_ratio': lambda curr_time: lambda task: task.get_max_benefit() / task.get_duration(),
    'deadline': lambda task: task.get_deadline(),
    'deadline_profit': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_deadline(),
    'linear': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration() + (task.get_max_benefit() / task.get_deadline()),
}


def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing
    """
    """
    input:tasks
    output:order of tasks, final profit
    Start with a root
    create an array for greedy estimation of bound and it's sorted by ratio
    """
    pass


def bound():
    pass


class Node:
    def __init__(self, data, bound):
        self.left = None
        self.right = None
        self.data = data
        self.bound = bound


def simulated_annealing(tasks, temp):
    profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = EVAL_FUNCTIONS['deadline_profit']
    sequence = []
    time = 0
    profit = 0.0

    while len(tasks) > 0:
        top_ten = sorted(tasks, key=deadline(time), reverse=True)[:10]

        # Sort by the profit/duration
        best = sorted(top_ten, key=profit_margin(time), reverse=True)[0]

        # Random choice out of possible options
        random_choice = top_ten[random.randint(0, len(top_ten)-1)]

        # Determine if the time has gone over the deadline
        overtime = time - best.get_deadline()

        # temp schedule
        t = temp/(time+1)

        # Difference in energy
        diff = best.get_late_benefit(overtime) - random_choice.get_late_benefit(overtime)

        # Annealing constant
        anneal = math.exp(-diff/t)
        choice = best
        if diff >= 0 and random.random() < anneal:
            choice = random_choice

        if time + choice.get_duration() > 1440:
            time -= choice.get_duration()
            break
        # Add expected profit from igloo
        profit += choice.get_late_benefit(overtime)

        # Remove task from tasks
        tasks.remove(choice)

        # Add the duration of the task to the time
        time += choice.get_duration()

        # Add the task to the sequence
        sequence.append(choice.get_task_id())

    assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
    return sequence, profit