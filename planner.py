from collections import defaultdict

from balancer import (
    READ_WEIGHT,
    PLUS_WEIGHT,
    MINUS_WEIGHT,
    MUL_WEIGHT,
    DIV_WEIGHT,
    OPERATOR_WEIGHT
)

COLUMN_WIDTH = 15

class Planner:
    def __init__(self, proc=None, layers=1):
        self.tree = None
        # self.proc = Proc(layers)
        # self.queues = [Queue() for i in range(layers)]
        self.proc = PipelineCpu(layers)
        self.operations = {}
        self.task_id = 0

    def prepare(self, balanced_tree):
        self.tree = self.extract_operations(balanced_tree)
        print("ok")

    def extract_operations(self, root_node):


        operation_node = OperationNodeFab(self.task_id, root_node)

        if isinstance(operation_node, Data):
            return operation_node


        self.operations[self.task_id] = operation_node
        self.task_id += 1

        operation_node.left = self.extract_operations(root_node.left_child)
        operation_node.right = self.extract_operations(root_node.right_child)



        return operation_node

    def enqueue_tasks(self):
        next_load_operation_value = None

        while True:
            ready_ops = [o for o in self.operations.values() if o.is_ready]
            ready_ops.sort(key=lambda o: o.id)
            if not ready_ops:
                break

            next_load_ops = [o for o in ready_ops if o.value == next_load_operation_value]
            next_load_operation_changed = not bool(next_load_ops)

            if next_load_operation_changed:

                ops_counter = defaultdict(int)
                for o in ready_ops:
                    ops_counter[o.value] += 1
                next_load_operation_value = max(ops_counter.items(), key=lambda x: x[1])[0]
                print(f"switched to '{next_load_operation_value}'")
                next_load_ops = [o for o in ready_ops if o.value == next_load_operation_value]

            next_op = next_load_ops.pop(0)
            self.proc.load(next_op)
            print(f"load process {next_op.id}: {next_op.value} {next_op.node}")
            next_op.is_done = True

        self.proc.run()



class Operation:
    def __init__(self, id, node):
        self.id = id
        self.value = node._data
        self.node = node
        self.left = None
        self.right = None
        self._done = False

    @property
    def is_ready(self):
        return (not self.is_done) and self.left.is_done and self.right.is_done

    @property
    def is_done(self):
        return self._done and self.left.is_done and self.right.is_done

    @is_done.setter
    def is_done(self, value):
        self._done = value



class PlusOperation(Operation):
    value = "+"
    weight = PLUS_WEIGHT

class MinusOperation(Operation):
    value = "-"
    weight = MINUS_WEIGHT

class MultiplyOperation(Operation):
    value = "*"
    weight = MUL_WEIGHT

class DivideOperation(Operation):
    value = "/"
    weight = DIV_WEIGHT

class Data(Operation):
    def __init__(self, id, node):
        super(Data, self).__init__(id, node)
        self.id = -1
        self.node = node._data
        self.weight = READ_WEIGHT

    @property
    def is_ready(self):
        return True

    @property
    def is_done(self):
        return True

class OperationNodeFab(Operation):
    operations = {
        "+": PlusOperation,
        "-": MinusOperation,
        "*": MultiplyOperation,
        "/": DivideOperation,
    }

    def __new__(cls, id, node, *args, **kwargs):
        operator = node._data
        OperationKlass = OperationNodeFab.operations.get(operator, Data)
        return OperationKlass(id, node, *args, **kwargs)

#
# class Queue():
#     def __init__(self):
#         self._queue = []
#
#     def enqueue_task(self, task):
#         for i in range(task.weight):
#             self._queue.append(task)




class PipelineCpu:
    def __init__(self, layers):
        self.cores = [Core() for i in range(layers)]
        self.queue = []

    @property
    def operation_type(self):
        for c in self.cores:
            if c.task:
                return c.task.value
        return None
    
    @property
    def operation_weight(self):
        return OPERATOR_WEIGHT.get(self.operation_type, 0)



    @property
    def is_free(self):
        return not bool(self.operation_type)

    def load(self, task):
        self.queue.append(task)

    def rotate_tasks(self):
        if self.cores[-1].task:
            self.cores[-1].task.is_done = True

        for i in reversed(range(len(self.cores) - 1)):
            self.cores[i+1].task = self.cores[i].task
        self.cores[0].task = None

    def run(self):
        time = 0
        while self.queue or not self.is_free:
            self.rotate_tasks()
            
            
            if self.queue:
                task = self.queue[0]
                if task.value == self.operation_type or self.is_free:
                    self.queue.pop(0)
                    self.cores[0].task = task

            print(f"{time:03d}: {self.cores_str()}")
            time += self.operation_weight

        max_time = time
        print(f"max_time: {max_time}")



    def cores_str(self):
        return "|".join([str(c) for c in self.cores])





class Core:
    def __init__(self):
        self.working = False
        self.task = None

    @property
    def is_working(self):
        return bool(self.task)

    def __str__(self):
        if not self.task:
            return "_" * COLUMN_WIDTH

        s = f"__{self.task.value}: (id={self.task.id:02d})"
        return f"{s}{'_' * (COLUMN_WIDTH - len(s))}"
