import math
import os
import Task
import treelib
import copy
import random
#duration: max 60
#deadline: max 1440
#profit: max 99
#factor = f(deadline)

#each node has data which is a list [identifier , bound, current profit, height, (to be added)times keep doing great(how many 3 braches)]


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
        self.height = len(tasks)
        self.sorted_list = self.set_up(tasks)
        self.bound = self.set_bound(tasks)
        self.tasks = tasks
        self.factor = 1
        self.marshal()
        self.root = self.tree.create_node(identifier = '-1', data = ['-1' , self.bound, 0, 0])
        self.best_order = []
        self.maximum = 3*self.height
        self.num_nodes = 1
        # when we update self.bound we memorize that node, because the leave node we want is in its subtree
        self.subtree_node = self.root
        # the last node updated self.bound has priviledge to hold at least one branch

    def set_up(self, tasks: list):
        profit_margin = lambda task: task.get_max_benefit() / task.get_duration()
        sorted_tasks = sorted(tasks, key=profit_margin, reverse=True)
        return sorted_tasks

    def simulated_annealing(self,tasks, temp):
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
            tasks.remove(choice)

            # Add the duration of the task to the time
            time += choice.get_duration()

            # Add the task to the sequence
            sequence.append(choice.get_task_id())

        assert time <= 1440, f'Tasks time {time} exceed the limit of 1440'
        return sequence, profit


    def set_bound(self,tasks: list):
        profit_margin = lambda task: task.get_max_benefit() / task.get_duration()
        deadline = lambda task: task.get_deadline()
        sequence = []
        time = 0
        profit = 0.0
        while time <= 1440 and len(tasks) > 0 :
            # Sort by the profit/duration
            top_ten_sorted = sorted(tasks, key=profit_margin, reverse=True)[:10]

            # Sort by the largest deadline
            best = sorted(top_ten_sorted, key=deadline, reverse=True)[0]

            # Remove task from tasks
            tasks.remove(best)

            # Add the task to the sequence
            sequence.append(best.get_task_id())

            # Add the duration of the task to the time
            time += best.get_duration()

            # Determine if the time has gone over the deadline
            overtime = time - best.get_deadline()

            # Apply profit decay
            if overtime > 0:
                decay = -0.0170 * overtime
                profit += best.get_max_benefit() * math.exp(decay)

            # Add profit without discount if task accomplished before deadline
            else:
                profit += best.get_max_benefit()
        return profit
    # used for node other than root
    def get_bound(self, task: Task):
        node = self.tree.get_node(task.task_id())

    def show(self):
        self.tree.show()
        return

    def marshal(self):
        sum_profit = 0
        sum_duration = 0
        for i in range(self.height):
            sum_profit += self.sorted_list[i].get_max_benefit()
            sum_duration += self.sorted_list[i].get_duration()
        if sum_duration == 0:
            sum_duration += 1
        factor = sum_profit/sum_duration
        if factor < 1.6:
            #in this case profit too small
            self.factor = factor/1.6
            for i in range(self.height):
                self.sorted_list[i].modify_profit(self.sorted_list[i].get_max_benefit()*1.6/factor)
        return

    def union_tasks(self, tasks1, tasks2):
        result = []
        for i in tasks1:
            result.append(i)
        for j in tasks2:
            if j not in tasks1:
                result.append(j)
        return result

    def heuristic(self, task: Task):
        return math.exp(3*task.get_max_benefit()/task.get_duration()) + task.get_duration() + \
        task.get_max_benefit()

    def branch_beuristic(self, task: Task):
        return task.get_deadline()
        #return sorted(tasks, key = lambda value: value.get_deadline(),reverse = True)

    def assign_branch(self, node):
        if self.num_nodes >= self.maximum:
            if node.data[2] > 0.95*self.bound*(node.data[3]/self.height):
                return 1
            else:
                return 0
        if node.data[3] <= int(self.height*0.02):
            return 3
        else:
            if node.data[2] > self.bound*(node.data[3]/self.height):
                return 2
            elif node.data[2] > 0.9*self.bound*(node.data[3]/self.height):
                return 1
            #elif node.data[2] > 0.7*self.bound*(node.data[3]/self.bound):
            #    return 1
            else:
                return 0
    def reurn_profit(self, available_tasks, current_time, node): # return the max profit
        # first generate all branches that can be taken by heuristic
        # return when time is used, return the current profit for this node

        if current_time > 1440:
            parent_node = self.tree.parent(node.data[0])
            return parent_node.data[2]
        # calculate the bound
        if node.data[2] >= self.bound:
            self.subtree_node = node
            self.bound = node.data[2]
        # should rerun for this case
        if len(available_tasks) == 0:
            return node.data[2]
        #sort_heuristic = sorted(available_tasks, key = lambda task: self.heuristic(task))[:max(1,10 - node.data[3])]
        #sort_heuristic = sorted(available_tasks, key = lambda task: self.heuristic(task))[:max(1,3 - node.data[3])]
        sort_heuristic = []
        sort_branch = []
        #sort_branch = self.branch_beuristic(available_tasks)[:max(1, 10 - node.data[3])]
        if node.data[3] < 1:
            # the available tasks we feed in is already the sorted one
            sort_heuristic = sorted(available_tasks, key = lambda task: self.heuristic(task))[:2]
            sort_branch = sorted(available_tasks, key = lambda task: self.branch_beuristic(task))[:2]
        else:
            sort_heuristic = available_tasks[:2]
            sort_branch = sorted(available_tasks, key=lambda task: self.branch_beuristic(task))[:2]
        union_list = sort_heuristic + sort_branch
        all_branch = []
        [all_branch.append(x) for x in union_list if x not in all_branch]
        ##
        t = self.assign_branch(node)
        all_branch = all_branch[:self.assign_branch(node)]
        ##
        if all_branch == []:
            result = node.data[2]
            self.tree.remove_node(node.data[0])
            self.num_nodes -= 1
            return result
        count = 0
        for i in range(len(all_branch)):

            # bound not implemented
            new_available_tasks = copy.deepcopy(available_tasks)
            pop_task = new_available_tasks.pop(i)
            if current_time + pop_task.get_duration() < 1440:
                count += 1
                new_node = self.tree.create_node(identifier = node.data[0] + '-' + str(pop_task.get_task_id()), parent = node.data[0]
                                             , data =[node.data[0] + '-' + str(pop_task.get_task_id()),
         self.bound, node.data[2] + pop_task.get_late_benefit(current_time + pop_task.get_duration() - pop_task.get_deadline()) ,node.data[3] + 1])
                self.num_nodes += 1
                self.reurn_profit(new_available_tasks, current_time + pop_task.get_duration(), new_node)
        if count == 0:
            return node.data[2]
    def result(self):
        self.reurn_profit(self.sorted_list, 0, self.tree.get_node('-1'))
        return self.bound*self.factor

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