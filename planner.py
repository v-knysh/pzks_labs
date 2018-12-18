from balancer import READ_WEIGHT, PLUS_WEIGHT, MINUS_WEIGHT, MUL_WEIGHT, DIV_WEIGHT, BalancerNode


class Planner:
    def __init__(self, proc=None):
        self.tree = None
        self.proc = proc
        self.operations = {}
        self.task_id = 0

    def prepare(self, balanced_tree):
        self.tree = self.extract_operations(balanced_tree)
        print("ok")

    def extract_operations(self, root_node):


        operation_node = OperationNodeFab(self.task_id, root_node)

        # if root_node.right_child.type != LexemNode.OPERATOR and root_node.left_child.type != LexemNode.OPERATOR:
        #     operation_node.left = Data(root_node.left_child._data)
        #     operation_node.right = Data(root_node.right_child._data)
        #     return operation_node
        if isinstance(operation_node, Data):
            return operation_node


        self.operations[self.task_id] = operation_node
        self.task_id += 1

        operation_node.left = self.extract_operations(root_node.left_child)
        operation_node.right = self.extract_operations(root_node.right_child)



        return operation_node



class Operation:
    def __init__(self, id, node):
        self.id = id
        self.value = node._data
        self.node = node
        self.left = None
        self.right = None
        self._ready = False

    @property
    def ready(self):
        return self.left.ready and self.right.ready

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
    def ready(self):
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







class Proc:
    def __init__(self):
        self.cores = []

class Core:
    def __init__(self):
        self.query = Query()

class Query:
    pass