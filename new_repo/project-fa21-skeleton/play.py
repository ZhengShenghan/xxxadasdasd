import math
import treelib
import Task
import queue
import copy
import random


def diff_list(tasks, list2: list):
    # list2 is a true subset of list1
    list_buffer = copy.deepcopy(tasks)
    count = 0
    delete_list = []
    for i in range(len(tasks) - 1, -1, -1):
        if list_buffer[i].get_task_id() in list2:
            del list_buffer[i]
            count += 1
            if count == len(list2):
                return list_buffer
if __name__ == '__main__':
    task1 = Task.Task(0, 1, 2, 3.0)
    task2 = Task.Task(1, 1, 2, 3.0)
    task3 = Task.Task(2, 1, 2, 3.0)
    task4 = Task.Task(3, 1, 2, 3.0)
    f = diff_list([task1,task2,task3,task4],[0,3])
    tree = treelib.Tree()
    tree.create_node(identifier='0',data=[1])
    tree.create_node(identifier='1', parent='0',data = [1])
    tree.create_node(identifier='3', parent='0',data = [2])
    tree.show()
    c = random.sample(range(0,5),5)
    print(1)
    b = 2
    '''
    tree.create_node(identifier = '0',data = task1)

    tree.create_node(identifier = '1', parent = '0',data = task2)
    tree.create_node(identifier = '2', parent='0', data=task3)
    #root = tree.leaves()
    q.put(task1)
    q.put(task2)
    q.put(task3)
    b = q.get()
    print(b)
    for i in range(q.qsize()):
        print(q.get())
    print(q.qsize())

    e = [1, 2, 3, 4, 5]
    for i in range(1, len(e)):
        f = copy.deepcopy(e)
        f.pop(i)
        tree.create_node(identifier = str(i+1), parent= '0', data = f)

    tree.show()'''