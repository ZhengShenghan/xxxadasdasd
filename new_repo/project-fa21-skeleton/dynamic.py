from solver import EVAL_FUNCTIONS

def dp_solver(tasks):
    profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
    deadline = EVAL_FUNCTIONS['deadline']

    sorted_tasks = sorted(tasks, key=deadline, reverse=False)
    mem = {}
    sequence = dp_helper(sorted_tasks, 0, 0, mem)
    return sequence


def dp_helper(tasks, i, time, mem):
    if i == len(tasks)-1:
        last_task = tasks[-1]
        if time + last_task.get_duration() > 1440:
            return 0, [-1]
        overtime = time + last_task.get_duration() - last_task.get_deadline()
        return last_task.get_late_benefit(overtime), [last_task.get_task_id()]

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
        new_s = [curr_task.get_task_id()]
        for t in with_current[1]:
            new_s.append(t)
        with_current = (new_p, new_s)

    without_current = dp_helper(tasks, i + 1, time, mem)
    mem[(curr_task, time)] = max([with_current, without_current], key=lambda x: x[0])
    return mem[(curr_task, time)]
