from builtins import enumerate

from lexem import BaseLexem, LexemGroup, LexemAnalyser, NumberLexem, VariableLexem, OperatorLexem, BracketLexem, Lexem

NUMBER_WEIGHT = 0
READ_WEIGHT = 1
PLUS_WEIGHT = 2
MINUS_WEIGHT = 3
MUL_WEIGHT = 4
DIV_WEIGHT = 5

OPERATOR_WEIGHT = {
    '+': PLUS_WEIGHT,
    '-': MINUS_WEIGHT,
    '*': MUL_WEIGHT,
    '/': DIV_WEIGHT,
}

OPERATOR_PRIORITY = {
    '+': 0,
    '-': 1,
    '*': 2,
    '/': 3,
}
READ_DATA_PRIORITY = 4


class Node:
    OPERATOR = "NODE_OPERATOR"
    DATA = "NODE_DATA"
    GROUP = "NODE_GROUP"

    def __init__(self, name, left_child=None, right_child=None, weight=0, priority=0):
        self._data = name
        self.left_child = left_child
        self.right_child = right_child
        self._weight = weight
        self.priority = priority

        self.type = Node.OPERATOR if name in OPERATOR_PRIORITY else Node.DATA
    @property
    def name(self):
        res = [
            f"{self.left_child.name if self.left_child else ''}",
            f"{self._data}"
            f"{self.right_child.name if self.right_child else ''}"
        ]
        res = " ".join(res)
        if self.type is Node.GROUP:
            res = f"({res})"
        return res


    @property
    def weight(self):
        _weight = self._weight
        _weight += self.right_child.weight if self.right_child else 0
        _weight += self.left_child.weight if self.left_child else 0
        return _weight

    @classmethod
    def create_from_lexem(cls, lexem):
        if isinstance(lexem, NumberLexem):
            weight = NUMBER_WEIGHT
            priority = READ_DATA_PRIORITY
        elif isinstance(lexem, VariableLexem):
            weight = READ_WEIGHT
            priority = READ_DATA_PRIORITY
        elif isinstance(lexem, OperatorLexem):
            weight = OPERATOR_WEIGHT.get(lexem.token)
            priority = OPERATOR_PRIORITY.get(lexem.token)

        return cls(
            name=lexem.token,
            weight=weight,
            priority=priority,
        )

    def __repr__(self):
        return f"{self.name} ({self.weight})"

class SyntaxAnalyzer:
    def __init__(self):
        pass

    def get_node(self, lexem):
        if isinstance(lexem, LexemGroup):
            node = self.parse_group(lexem)
            node.type = Node.GROUP
            node.priority = READ_DATA_PRIORITY
            return node
        node = Node.create_from_lexem(lexem)
        return node


    def parse_group(self, group):
        node_list = []
        for lexem in group.lexems:
            if isinstance(lexem, BracketLexem):
                continue
            node_list.append(self.get_node(lexem))
        nodes = []
        for i, node in enumerate(node_list):
            if node._data == "/":
                nodes.append(self.get_node(Lexem("*", "OPERATOR")))
                nodes.append(self.get_node(Lexem(1, "NUMBER")))

            if node._data == "-":
                nodes.append(self.get_node(Lexem("+", "OPERATOR")))
                nodes.append(self.get_node(Lexem(0, "NUMBER")))

            nodes.append(node)

        root_node = self.parse_list(nodes)

        return root_node

    def print_tree(self, node):
        rows = self.str_node(node)
        max_len = max([len(r) for r in rows])
        rows = [f'{r}{" "*(max_len - len(r))}' for r in rows]

        transposed = [[] for _ in range(max_len)]
        for j, r in enumerate(rows):
            for i, s in enumerate(r):
                transposed[i].append(s)
        rows = [' '.join(r) for r in transposed]
        for r in rows:
            print(r)

        print('----------------------------------------------')


    def str_node(self, node):
        if node is None:
            return []
        res = []

        res.extend(self.str_node(node.left_child)),
        res.append(node._data),
        res.extend(self.str_node(node.right_child)),
        return [f'_{s}' for s in res]


    def parse_list(self, node_list):
        if len(node_list) == 1:
            return node_list[0]
        elif len(node_list) == 0:
            return None


        if len(node_list) == 3:
            central_node = node_list[1]
            central_node.left_child = node_list[0]
            central_node.right_child = node_list[2]
            return central_node

        central_index = self.get_central_node(node_list)
        central_node = node_list[central_index]

        central_node.left_child = self.parse_list(node_list[0:central_index])
        central_node.right_child= self.parse_list(node_list[central_index+1:])

        return central_node

    def get_central_node(self, node_list):

        sum_weight = sum(n.weight for n in node_list)
        min_priority = min((n.priority for n in node_list))

        weight_dir = 0
        for index_dir, central_node_dir in enumerate(node_list):

            weight_dir += central_node_dir.weight
            if weight_dir >= sum_weight / 2 and central_node_dir.priority == min_priority and central_node_dir.type == Node.OPERATOR:
                break

        weight_rev = 0
        for i, central_node_rev in enumerate(node_list[::-1]):

            index_rev = len(node_list) - 1- i
            weight_rev += central_node_rev.weight
            if weight_rev >= sum_weight / 2 and central_node_rev.priority == min_priority and central_node_rev.type == Node.OPERATOR:
                break

        dir_criteria = (weight_dir - (sum_weight / 2)) * (1000 * int(central_node_dir.type != Node.OPERATOR))
        rev_criteria = (weight_rev - (sum_weight / 2)) * (1000 * int(central_node_rev.type != Node.OPERATOR))

        index = index_rev if rev_criteria < dir_criteria else index_dir
        return index

class BracketsOpener:

    def max_depth(self, root_node):
        if not(root_node.right_child and root_node.left_child):
            return 0

        return max(self.max_depth(root_node.right_child), self.max_depth(root_node.left_child)) + 1

    def open_brackets(self, root_node):
        while self.max_depth(root_node) > 1:
            root_node = self.open_brackets_step(root_node)

    def open_brackets_step(self, root_node):
        if not(root_node.right_child and root_node.left_child):
            return [root_node]
        node_list = []
        if root_node._data == '+' or root_node._data == '-':
            node_list.extend(self.open_brackets(root_node.left_child))

            node_list.append(Node(
                root_node._data,
                weight=OPERATOR_WEIGHT.get(root_node._data, 0),
                priority=OPERATOR_PRIORITY.get(root_node._data, 0),
            ))
            node_list.extend(self.open_brackets(root_node.right_child))

        # if root_node._data == '*':

        return node_list




