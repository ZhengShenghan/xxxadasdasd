import FuncSets
import Task
import queue
import copy
import FuncSets_simulated_annealing

def diff_list(list1: list, list2: list):
    # list2 is a true subset of list1
    list_buffer = copy.deepcopy(list1)
    for x in list2:
        list_buffer.remove(x)

    return list_buffer

if __name__ == '__main__':
    task1 = Task.Task(0, 1000, 100, 3.0)
    task2 = Task.Task(1, 1000, 500, 3.0)
    task3 = Task.Task(2, 700, 200, 3.0)
    task4 = Task.Task(3, 500, 200, 3.0)
    task5 = Task.Task(4, 200, 600, 3.0)
    tree = FuncSets_simulated_annealing.branch_and_bound([task1,task2,task3,task4])
    print(tree.result())
    print(tree.return_sequence())