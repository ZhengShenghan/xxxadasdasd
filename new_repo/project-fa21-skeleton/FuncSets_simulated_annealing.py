import math
import os
import Task
import treelib
import copy
import random
import queue
#duration: max 60
#deadline: max 1440
#profit: max 99
#factor = f(deadline)

#each node has data which is a list [identifier , current profit, height, endtime(to be added)times keep doing great(how many 3 braches)]


#tasks [[id deadline duration profit]...]

EVAL_FUNCTIONS = {
    'adv_profit_ratio': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration(),
    'profit_ratio': lambda curr_time: lambda task: task.get_max_benefit() / task.get_duration(),
    'deadline': lambda task: task.get_deadline(),
    'deadline_profit': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_deadline(),
    'linear': lambda curr_time: lambda task: task.get_late_benefit((curr_time+task.get_duration())-task.get_deadline()) / task.get_duration() + (task.get_max_benefit() / task.get_deadline()),
}

class branch_and_bound:
    def __init__(self, tasks):
        self.tree = treelib.Tree()
        self.best_profit = 0
        self.factor = 1
        self.height = len(tasks)
        # we have 3 levels divided by total time which is 1440
        #self.best_each_level = [0]
        self.root = self.tree.create_node(identifier='-1', data=['-1', 0, 0, 0])
        self.T = self.naive_simulated_annealing(tasks, 2000)
        self.T = 1/self.T
        self.L = min(10, int(self.height/10))
        self.queue = queue.Queue()
        self.tasks = tasks
        self.marshal()
        self.queue.put(self.root)
        self.num_nodes = 1
        # when we update self.bound we memorize that node, because the leave node we want is in its subtree
        self.subtree_node = self.root
        # the last node updated self.bound has priviledge to hold at least one branch
    def naive_simulated_annealing(self, tasks, temp):
        profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
        deadline = EVAL_FUNCTIONS['deadline_profit']
        time = 0
        profit = 0.0
        buffer_tasks = copy.deepcopy(tasks)
        sequence = []
        while len(tasks) > 0:
            top_ten = sorted(buffer_tasks, key=deadline(time), reverse=True)[:10]
            if top_ten == []:
                break
            # Sort by the profit/duration
            best = sorted(top_ten, key=profit_margin(time), reverse=True)[0]

            # Random choice out of possible options
            random_choice = top_ten[random.randint(0, len(top_ten) - 1)]

            # Determine if the time has gone over the deadline
            overtime = time - best.get_deadline()

            # temp schedule
            t = temp / (time + 1)

            # Difference in energy
            diff = best.get_late_benefit(overtime) - random_choice.get_late_benefit(overtime)

            # Annealing constant
            anneal = math.exp(-diff / t)
            choice = best
            if diff >= 0 and random.random() < anneal:
                choice = random_choice

            if time + choice.get_duration() > 1440:
                time -= choice.get_duration()
                break
            # Add expected profit from igloo
            profit += choice.get_late_benefit(overtime)

            # Remove task from tasks
            buffer_tasks.remove(choice)

            # Add the duration of the task to the time
            time += choice.get_duration()

            # Add the task to the sequence
            sequence.append(choice.get_task_id())
        name = '-2'
        self.best_profit = profit
        for x in sequence:
            name = name + '-' + str(x)
        self.tree.create_node(identifier = name, parent = '-1', data = [name, profit, 1, 1440])
        assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
        return profit

    def simulated_annealing(self, tasks, time_constraint, start_time, node):
        temp = 2000
        profit_margin = EVAL_FUNCTIONS['adv_profit_ratio']
        deadline = EVAL_FUNCTIONS['deadline_profit']
        runtime = 0
        pre_profit = 0
        T_ini = 0
        T_end = 0
        k = 0.95
        while runtime < self.L:
            sequence = []
            time = 0
            profit = 0.0
            input_tasks = copy.deepcopy(tasks)
            while len(input_tasks) > 0:


                top_ten = sorted(input_tasks, key=deadline(time), reverse=True)[:10]
                add_rand = random.sample(range(0, len(input_tasks)), max(1, int(len(input_tasks)/20)))
                for x in add_rand:
                    if self.tasks[x] not in top_ten:
                        top_ten.append(input_tasks[x])
                best = sorted(top_ten, key=profit_margin(time), reverse=True)[0]

                # Random choice out of possible options
                random_choice = top_ten[random.randint(0, len(top_ten) - 1)]

                # Determine if the time has gone over the deadline
                overtime = start_time + time - best.get_deadline()
                
                # temp schedule
                t = temp / (start_time + time + 1)

                # Difference in energy
                diff = best.get_late_benefit(overtime) - random_choice.get_late_benefit(overtime)

                # Annealing constant
                anneal = math.exp(-diff / t)
                choice = best
                if diff >= 0 and random.random() < anneal:
                    choice = random_choice

                if start_time + time + choice.get_duration() > time_constraint:
                    time -= choice.get_duration()
                    break
                # Add expected profit from igloo

                profit += choice.get_late_benefit(overtime)

                #self.best_each_level.append(profit)

                # Remove task from tasks
                input_tasks.remove(choice)

                # Add the duration of the task to the time
                time += choice.get_duration()

                # Add the task to the sequence
                #sequence.append(choice.get_task_id())
                sequence.append(choice.get_task_id())
            if runtime == 0:
                pre_profit = profit
                T_ini = 1/profit
                T_end = 1/(profit + 0.15*profit)
                new_node = self.tree.create_node(identifier = node.data[0] + self.generate_id(sequence), parent = node.data[0],
                                      data = [node.data[0] + self.generate_id(sequence), profit, node.data[2] + 1, node.data[3] + time])
                self.queue.put(new_node)
                self.num_nodes += 1
            else:
                # add another while loop
                if T_end > 1/profit:
                    break
                if self.metroplis_rule(1/profit, 1/pre_profit, k, T_ini) == 1:
                    new_node = self.tree.create_node(identifier=node.data[0] + self.generate_id(sequence), parent=node.data[0],
                                          data=[node.data[0] + self.generate_id(sequence), profit, node.data[2] + 1, node.data[3] + time])
                    self.queue.put(new_node)
                    self.num_nodes += 1
            runtime += 1
        #assert time <= time_constraint, f'Tasks time {time} exceed the limit of {time_constraint}'
        #return sequence, profit

    def generate_id(self, list_id :list):
        result = ''
        for i in range(len(list_id)):
            result += '-' + str(list_id[i])
        return result

    def metroplis_rule(self, E_1, E_2, k, T):
        # E_1 is the E(t+1),E_2 is E(t), k is the decreasing speed
        # return 0 means reject the new solution, return 1 means accept the new solution
        if E_1 < E_2:
            return 1
        else:
            choice = random.uniform(0,1)
            if choice <= math.exp(-(E_1 - E_2)/k*T):
                return 1
        return 0

    def show(self):
        self.tree.show()
        return

    def diff_list(self, tasks, list2: list):
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

    def marshal(self):
        sum_profit = 0
        sum_duration = 0
        for i in range(self.height):
            sum_profit += self.tasks[i].get_max_benefit()
            sum_duration += self.tasks[i].get_duration()
        if sum_duration == 0:
            sum_duration += 1
        factor = sum_profit/sum_duration
        if factor < 1.6:
            #in this case profit too small
            self.factor = factor/1.6
            for i in range(self.height):
                self.tasks[i].modify_profit(self.tasks[i].get_max_benefit()*1.6/factor)
        return

    def return_profit(self, node):
        # determine which input should be feeded into simulated anealing
        # feed in available tasks , set start time,
        if node.data[1] > self.best_profit:
            self.best_profit = node.data[1]
            self.subtree_node = node
        if self.queue.qsize() == 0:
            return node.data[1]
        input_node = self.queue.get()
        if input_node.data[2] == 0:
            self.simulated_annealing(self.tasks, int(1440/3), 0, input_node)
        else:
            name = input_node.data[0]
            name_list = name.split('-')[2:]
            for i in range(len(name_list)):
                name_list[i] = int(name_list[i])
            input_tasks = self.diff_list(self.tasks, name_list)
            if input_node.data[2] == 1:
                self.simulated_annealing(input_tasks, int(1440*2/3), input_node.data[3], input_node)
                #self.return_profit(input_tasks, node.data[3], input_node)
                self.return_profit(input_node)
            if input_node.data[2] == 2:
                self.simulated_annealing(input_tasks, 1440, input_node.data[3], input_node)
                #self.return_profit(input_tasks, node.data[3], input_node)
                self.return_profit(input_node)

    def result(self):
        self.return_profit(self.root)
        return self.best_profit*self.factor

    def return_sequence(self):
        if self.subtree_node == self.root:
            result = []
            for i in range(len(self.sorted_list)):
                result.append(self.sorted_list[i][0])
            self.best_order = result
            return result
        all_leaves = self.tree.leaves(self.subtree_node.data[0])
        for i in range(len(all_leaves)):
            node = all_leaves[i]
            if node.data[2] == self.bound:
                identifier = node.data[0]
                str_list = identifier.split('-')[2:]
                for j in range(len(str_list)):
                    str_list[j] = int(str_list[j])
                self.best_order = str_list
                return str_list
'''
    def lemma_order(self):
        list_of_time_stamp = []
        sum = 0
        for i in range(self.height):
            list_of_time_stamp.append(sum)
            sum += self.tasks[self.best_order[i]].data[2]
        for i in range(1, self.height):
            for j in range(i):
                if self.tasks[self.best_order[i]][1] >= self.tasks[self.best_order[i]]'''