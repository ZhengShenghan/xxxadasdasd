from solver import EVAL_FUNCTIONS


def dp_solver(tasks):
    profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = EVAL_FUNCTIONS['deadline']

    sorted_tasks = sorted(tasks, key=deadline, reverse=False)
    mem = {}
    profit, sequence = dp_helper(sorted_tasks, 0, 0, mem)
    sequence = list(filter((-1).__ne__, sequence))
    assert len(set(sequence)) == len(sequence), "Sequence contains duplicates"
    assert check_sequence(sequence) <= 1440, "Sequence duration too long"
    f_sequence = [task.get_task_id() for task in sequence]
    return profit, f_sequence


def dp_helper(tasks, i, time, mem):
    if i == len(tasks)-1:
        last_task = tasks[-1]
        if time + last_task.get_duration() > 1440:
            return 0, [-1]
        overtime = time + last_task.get_duration() - last_task.get_deadline()
        return last_task.get_late_benefit(overtime), [last_task]

    curr_task = tasks[i]

    # We have already seen this task
    if (curr_task, time) in mem:
        return mem[(curr_task, time)]

    current_time = time + curr_task.get_duration()
    overtime = current_time - curr_task.get_deadline()
    current_profit = curr_task.get_late_benefit(overtime)

    if current_time > 1440:
        with_current = 0.0, [-1]
    else:
        with_current = dp_helper(tasks, i + 1, current_time, mem)
        new_p = with_current[0] + current_profit
        new_s = [curr_task]
        for t in with_current[1]:
            new_s.append(t)
        with_current = (new_p, new_s)

    without_current = dp_helper(tasks, i + 1, time, mem)
    mem[(curr_task, time)] = max([with_current, without_current], key=lambda x: x[0])
    return mem[(curr_task, time)]


def check_sequence(sequence):
    time = 0
    for task in sequence:
        time += task.get_duration()
    return time
