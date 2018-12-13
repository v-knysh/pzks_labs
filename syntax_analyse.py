from syntax import LexemNode
from lexem import VariableLexem, NumberLexem, OperatorLexem


class BaseNode:
    def __init__(self, node=None, data=None, *args, **kwargs):
        self.left_child = None
        self.right_child = None
        self.children = []
        self.data = data
        self.operation = self.data

    # @property
    # def children(self):
    #     if self._children:
    #         return self._children
    #
    #     if self.right_child and self.left_child:
    #         return [self.right_child, self.left_child]
    #
    #     return []


class Node(BaseNode):
    @classmethod
    def from_lexem_node(cls, lexem_node, *args, **kwargs):
        klass = BaseNode

        if isinstance(lexem_node._lexem, (VariableLexem, NumberLexem)):
            klass = DataNode
        elif isinstance(lexem_node._lexem, (OperatorLexem)):
            klass = OperationNode

        return klass(
            node=lexem_node,
            data=lexem_node._lexem.token,
        )


class OperationNode(BaseNode):
    pass

class DataNode(BaseNode):
    def __init__(self, node=None, data=None, *args, **kwargs):
        super(DataNode, self).__init__(node, data, *args, **kwargs)
        self.data = data

    # @property
    # def positive_group(self):
    #     return [self]
    # @property
    # def negative_group(self):
    #     return []
    # @property
    # def multiplication_group(self):
    #     return [self]
    # @property
    # def division_group(self):
    #     return []

    def __repr__(self):
        return f"<{self.data}>"


class GroupNode(BaseNode):
    operation = "_"
    def __init__(self, node, data, *args, **kwargs):
        super(GroupNode, self).__init__(node, data, *args, **kwargs)

        self.left_children = []
        self.right_children = []
        self.dummy = DataNode(data="0")

    def remove_redundant(self, lst, redundant=0):
        redundant = self.dummy.data
        lst_new = []
        redundant_node = None
        for d_node in lst:
            if d_node.data != redundant:
                lst_new.append(d_node)
        if not lst_new:
            lst_new.append(self.dummy)
        lst.clear()
        lst.extend(lst_new)
        return lst


class MultiplyNode(GroupNode):
    operation = "*"
    def __init__(self, node, data, *args, **kwargs):
        super(MultiplyNode, self).__init__(node, data, *args, **kwargs)
        self.multiplication_group = self.left_children
        self.division_group= self.right_children

        self.dummy = DataNode(data="1")

        self.left_children.append(self.dummy)
        self.right_children.append(self.dummy)

    @property
    def positive_group(self):
        return [self]
    @property
    def negative_group(self):
        return []

    def add_children(self, operation, left_node, right_node):
        if operation == "*":
            if isinstance(left_node, MultiplyNode):
                self.multiplication_group.extend(left_node.multiplication_group)
                self.division_group.extend(left_node.division_group)
            else:
                self.multiplication_group.append(left_node)

            if isinstance(right_node, MultiplyNode):
                self.multiplication_group.extend(right_node.multiplication_group)
                self.division_group.extend(right_node.division_group)
            else:
                self.multiplication_group.append(right_node)

        elif operation == "/":
            if isinstance(left_node, MultiplyNode):
                self.multiplication_group.extend(left_node.division_group)
                self.division_group.extend(left_node.multiplication_group)
            else:
                self.multiplication_group.append(left_node)
                # self.division_group.append(left_node)

            if isinstance(right_node, MultiplyNode):
                self.multiplication_group.extend(right_node.division_group)
                self.division_group.extend(right_node.multiplication_group)
            else:
                self.division_group.append(right_node)

        self.multiplication_group = self.remove_redundant(self.multiplication_group)
        self.division_group= self.remove_redundant(self.division_group)

    def __str__(self):
        return f"[({'*'.join([str(s) for s in self.multiplication_group])}) / ({'*'.join([str(s) for s in self.division_group])})]"



class SumNode(GroupNode):
    operation = "+"
    def __init__(self, node, data, *args, **kwargs):
        super(SumNode, self).__init__(node, data, *args, **kwargs)
        self.positive_group = self.left_children
        self.negative_group= self.right_children

        self.dummy = DataNode(data="0")

        self.left_children.append(self.dummy)
        self.right_children.append(self.dummy)



    def add_children(self, operation, left_node, right_node):
        if operation == "+":
            if isinstance(left_node, SumNode):
                self.positive_group.extend(left_node.positive_group)
                self.negative_group.extend(left_node.negative_group)
            else:
                self.positive_group.append(left_node)

            if isinstance(right_node, SumNode):
                self.positive_group.extend(right_node.positive_group)
                self.negative_group.extend(right_node.negative_group)
            else:
                self.positive_group.append(right_node)

        elif operation == "-":
            if isinstance(left_node, SumNode):
                self.positive_group.extend(left_node.negative_group)
                self.negative_group.extend(left_node.positive_group)
            else:
                self.positive_group.append(left_node)

            if isinstance(right_node, SumNode):
                self.positive_group.extend(right_node.negative_group)
                self.negative_group.extend(right_node.positive_group)
            else:
                self.negative_group.append(right_node)

        self.positive_group = self.remove_redundant(self.positive_group)
        self.negative_group = self.remove_redundant(self.negative_group)

    def __str__(self):
        return f"({'+'.join([str(s) for s in self.positive_group])} - {'-'.join([str(s) for s in self.negative_group])})"

OPERATION_NODES = {
    "+": SumNode,
    '-': SumNode,
    "*": MultiplyNode,
    '/': MultiplyNode,
}

class SyntaxTree:
    def __init__(self):
        pass

    def from_lexem_tree(self, root_node):

        node = Node.from_lexem_node(root_node)

        if isinstance(node, DataNode):
            return node


        left_node = self.from_lexem_tree(root_node.left_child)
        right_node = self.from_lexem_tree(root_node.right_child)

        node.left_child = left_node
        node.right_child = right_node

        # self.open_brackets(node)

        return node


    def open_brackets(self, root_node):

        left_node = root_node.left_child
        right_node = root_node.right_child

        if not (left_node or right_node):
            return root_node

        left_node = self.open_brackets(left_node)
        right_node = self.open_brackets(right_node)

        # if (isinstance(right_node, DataNode) and isinstance(left_node, DataNode)):

        NodeClass = OPERATION_NODES.get(root_node.data)
        node = NodeClass(root_node, root_node.data)
        node.add_children(root_node.data, left_node, right_node)
        return node



        return root_node







# class BracketsOpener:
#
#     def max_depth(self, root_node):
#         if not(root_node.right_child and root_node.left_child):
#             return 0
#
#         return max(self.max_depth(root_node.right_child), self.max_depth(root_node.left_child)) + 1
#
#     def open_brackets(self, root_node):
#         while self.max_depth(root_node) > 1:
#             root_node = self.open_brackets_step(root_node)
#
#     # def open_brackets_step(self, root_node):
    #     if not(root_node.right_child and root_node.left_child):
    #         return [root_node]
    #     node_list = []
    #     if root_node._data == '+' or root_node._data == '-':
    #         node_list.extend(self.open_brackets(root_node.left_child))
    #
    #         node_list.append(LexemNode(
    #             root_node._data,
    #             weight=OPERATOR_WEIGHT.get(root_node._data, 0),
    #             priority=OPERATOR_PRIORITY.get(root_node._data, 0),
    #         ))
    #         node_list.extend(self.open_brackets(root_node.right_child))
    #
    #     # if root_node._data == '*':
    #
    #     return node_list
