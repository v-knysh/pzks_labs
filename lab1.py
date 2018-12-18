# розкриття дужок, конвейєр зі статичним тактом
from lexem import LexemAnalyser, LexemGroup
from balancer import BalanceAnalyzer
from planner import Planner

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


    sa = BalanceAnalyzer()
    lexems_tree = sa.parse_group(lexem_group)



    sa.print_tree(lexems_tree)

    from regrouper import RegroupAnalyzer
    st = RegroupAnalyzer()
    syntax_tree = st.from_balancer_tree(lexems_tree)

    opened = st.regroup_children(syntax_tree)


    new_str = str(opened)
    print(new_str)
    lexem_analyzer = LexemAnalyser()
    lexems = lexem_analyzer.detect_lexems(new_str)

    lexem_group = lexem_analyzer.extract_bracket_groups(lexems)


    sa = BalanceAnalyzer()
    lexems_tree = sa.parse_group(lexem_group)

    p = Planner(lexems_tree)
    p.prepare()





    sa.print_tree(lexems_tree)




    # bo = BracketsOpener()
    # max_depth = bo.max_depth(syntax_tree)
    # print(max_depth)
    # opened = bo.open_brackets(syntax_tree)
    # syntax_tree_opened = sa.parse_list(opened)
    # sa.print_tree(syntax_tree_opened)



    print('ok')

