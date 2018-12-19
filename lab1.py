# розкриття дужок, конвейєр зі статичним тактом

from lexem import LexemAnalyser, LexemGroup
from balancer import BalanceAnalyzer
from planner import Planner
from regrouper import RegroupAnalyzer

from copy import copy





if __name__ == "__main__":
    # input_data = '1 * (2 + 3) * 4 + (1 - 2) * (5 + (5 + 7 * (8  + 9))) - 8'
    # input_data = '1 / (2 + 3) * 4 '
    # input_data = '1 + (2 - (3 + 4))'
    # input_data = '(4 + 2 * 3) * 5'
    # input_data = '(1 + 2 )'
    input_data = '(1 + 2 ) * (4 + 5)'
    # input_data = '(1 + ((2 - 3) + (1 - 3)) - (0 - 1 + (2 + 4))) - (4 - 5)'
    # input_data = input("input expression: ")

    print(input_data)

    lexem_analyzer = LexemAnalyser()
    lexems = lexem_analyzer.detect_lexems(input_data)

    lexem_group = lexem_analyzer.extract_bracket_groups(lexems)


    ba = BalanceAnalyzer()
    balanced_tree = ba.parse_group(lexem_group)



    ba.print_tree(balanced_tree)

    st = RegroupAnalyzer()
    syntax_tree = st.from_balancer_tree(balanced_tree)

    opened = st.regroup_children(syntax_tree)


    new_str = str(opened)
    print(new_str)
    lexem_analyzer = LexemAnalyser()
    lexems = lexem_analyzer.detect_lexems(new_str)

    lexem_group = lexem_analyzer.extract_bracket_groups(lexems)


    ba = BalanceAnalyzer()
    balanced_tree = ba.parse_group(lexem_group)

    p = Planner(layers=3)
    p.prepare(balanced_tree)
    p.enqueue_tasks()





    ba.print_tree(balanced_tree)




    # bo = BracketsOpener()
    # max_depth = bo.max_depth(syntax_tree)
    # print(max_depth)
    # opened = bo.open_brackets(syntax_tree)
    # syntax_tree_opened = sa.parse_list(opened)
    # sa.print_tree(syntax_tree_opened)



    print('ok')

