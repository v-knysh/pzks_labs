from syntax import LexemNode
from lexem import VariableLexem, NumberLexem, OperatorLexem

from itertools import product, chain

class BaseNode:
    def __init__(self, data=None, *args, **kwargs):
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
            data=lexem_node._lexem.token,
        )


class OperationNode(BaseNode):
    pass

class DataNode(BaseNode):
    def __init__(self, data=None, *args, **kwargs):
        super(DataNode, self).__init__(data, *args, **kwargs)
        self.data = data

    def __eq__(self, other):
        return (
            isinstance(other, BaseNode) and
            self.data == other.data
        )

    @property
    def positive_group(self):
        return [self]
    @property
    def negative_group(self):
        return []
    @property
    def multiplication_group(self):
        return [self]
    @property
    def division_group(self):
        return []

    def __repr__(self):
        return f"{self.data}"


class GroupNode(BaseNode):
    operation = "_"
    dummy = DataNode(data="0")

    def __init__(self, data, *args, **kwargs):
        super(GroupNode, self).__init__(data, *args, **kwargs)

        self.left_children = []
        self.right_children = []

    def __eq__(self, other):
        return (
            isinstance(other, GroupNode) and
            self.left_children == other.left_children and
            self.right_children == other.right_children
        )

    def remove_redundant(self, lst, redundant=0):
        redundant = self.dummy.data
        lst_new = []
        for d_node in lst:
            if d_node.data != redundant:
                lst_new.append(d_node)
        if not lst_new:
            lst_new.append(self.dummy)
        lst.clear()
        lst.extend(lst_new)
        return lst

    def regroup_operations(self):
        return self


class MultiplyNode(GroupNode):
    operation = "*"
    dummy = DataNode(data="1")
    killer = DataNode(data="0")

    def __init__(self, data=None, *args, **kwargs):
        super(MultiplyNode, self).__init__(data, *args, **kwargs)
        self.multiplication_group = self.left_children
        self.division_group= self.right_children


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
            self.multiplication_group.extend(left_node.multiplication_group)
            self.division_group.extend(left_node.division_group)

            self.multiplication_group.extend(right_node.multiplication_group)
            self.division_group.extend(right_node.division_group)


        elif operation == "/":
            self.multiplication_group.extend(left_node.division_group)
            self.division_group.extend(left_node.multiplication_group)

            self.multiplication_group.extend(right_node.division_group)
            self.division_group.extend(right_node.multiplication_group)


        self.multiplication_group = self.remove_redundant(self.multiplication_group)
        self.division_group= self.remove_redundant(self.division_group)

    def __str__(self):
        mul_part = ' * '.join([str(s) for s in self.multiplication_group])
        div_part = f"/ ({' * '.join([str(s) for s in self.division_group])})" if self.division_group != [self.dummy] else ""
        return f"({mul_part} {div_part})"


class SumNode(GroupNode):
    operation = "+"
    dummy = DataNode(data="0")



    def __init__(self, data=None, *args, **kwargs):
        super(SumNode, self).__init__(data, *args, **kwargs)
        self.positive_group = self.left_children
        self.negative_group= self.right_children


        self.left_children.append(self.dummy)
        self.right_children.append(self.dummy)


    # def add_children_sum(self):

    def add_children(self, operation, left_node, right_node):
        if operation == "+":
            self.positive_group.extend(left_node.positive_group)
            self.negative_group.extend(left_node.negative_group)

            self.positive_group.extend(right_node.positive_group)
            self.negative_group.extend(right_node.negative_group)


        elif operation == "-":
            self.positive_group.extend(left_node.negative_group)
            self.negative_group.extend(left_node.positive_group)

            self.positive_group.extend(right_node.negative_group)
            self.negative_group.extend(right_node.positive_group)

        self.positive_group = self.remove_redundant(self.positive_group)
        self.negative_group = self.remove_redundant(self.negative_group)

    def __str__(self):
        pos_part = ' + '.join([str(s) for s in self.positive_group])
        neg_part = f" - ({' + '.join([str(s) for s in self.negative_group])})" if self.negative_group!= [self.dummy] else ""
        return f"({pos_part} {neg_part})"

    # mul_part = '*'.join([str(s) for s in self.multiplication_group])
    # div_part = f"/ ({'*'.join([str(s) for s in self.division_group])})" if self.division_group != [self.dummy] else ""
    # return f"[{mul_part} {div_part}]"


class SumRegroupNode(SumNode):
    def add_children(self, operation, left_node, right_node):

        if operation == "*":

            left_pos = left_node.positive_group
            right_pos = right_node.positive_group

            left_neg = left_node.negative_group
            right_neg = right_node.negative_group

            pos_nodes = []
            for l, r in chain(product(left_pos, right_pos), product(left_neg, right_neg)):
                if l == MultiplyNode.killer or r == MultiplyNode.killer:
                    continue

                node = MultiplyNode(data="*")

                node.add_children("*", l, r)
                pos_nodes.append(node)

            neg_nodes = []
            for l, r in chain(product(left_pos, right_neg), product(left_neg, right_pos)):
                if l == MultiplyNode.killer or r == MultiplyNode.killer:
                    continue

                node = MultiplyNode(data="*")
                node.add_children("*", l, r)
                neg_nodes.append(node)

            self.positive_group.extend(pos_nodes)
            self.negative_group.extend(neg_nodes)

            self.remove_redundant(self.positive_group)
            self.remove_redundant(self.negative_group)







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

        return node


    def regroup_children(self, root_node):

        left_node = root_node.left_child
        right_node = root_node.right_child

        if not (left_node or right_node):
            return root_node

        left_node = self.regroup_children(left_node)
        right_node = self.regroup_children(right_node)

        NodeClass = self.get_node_class(root_node, left_node, right_node)
        node = NodeClass(root_node.data)
        node.add_children(root_node.data, left_node, right_node)

        regrouped = node.regroup_operations()

        return regrouped




    def get_node_class(self, root_node, left_node, right_node):
        if root_node.data in ['+', '-']:
            return SumNode

        if isinstance(right_node, SumNode) or isinstance(left_node, SumNode):
            return SumRegroupNode

        return MultiplyNode

