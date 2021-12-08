import solver
import random
import math

def basic_simulated_annealing(tasks, temp):
    profit_margin = solver.EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = solver.EVAL_FUNCTIONS['deadline_profit']
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


def basic_greedy(tasks):
    profit_margin = solver.EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = solver.EVAL_FUNCTIONS['deadline_profit']
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
