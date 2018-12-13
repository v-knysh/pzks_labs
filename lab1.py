# розкриття дужок, конвейєр зі статичним тактом
from lexem import LexemAnalyser, LexemGroup
from syntax import SyntaxAnalyzer

from copy import copy





if __name__ == "__main__":
    input_data = '1 * (2 + 3) * 4 + (a - b) * (5 + (5 + 7 * (8  + 9))) - a'
    # qwe = '1 / (2 + 3) * 4 '
    # qwe = '1 + (2 - (3 + 4))'
    # qwe = '(4 + 2 * 3) * 5'
    # qwe = '(1 + 2 ) * (4 - 5)'
    # qwe = '(1 + 2 ) * (4 - 5)'
    # qwe = '(1 + ((2 - 3) + (1 - 3)) - (0 - 1 + (2 + 4))) - (4 - 5)'
    # qwe = input("input expression: ")
    lexem_analyzer = LexemAnalyser()
    lexems = lexem_analyzer.detect_lexems(input_data)

    lexem_group = lexem_analyzer.extract_bracket_groups(lexems)


    sa = SyntaxAnalyzer()
    lexems_tree = sa.parse_group(lexem_group)



    sa.print_tree(lexems_tree)

    from syntax_analyse import SyntaxTree
    st = SyntaxTree()
    syntax_tree = st.from_lexem_tree(lexems_tree)

    opened = st.regroup_children(syntax_tree)


    print(opened)

    # bo = BracketsOpener()
    # max_depth = bo.max_depth(syntax_tree)
    # print(max_depth)
    # opened = bo.open_brackets(syntax_tree)
    # syntax_tree_opened = sa.parse_list(opened)
    # sa.print_tree(syntax_tree_opened)



    print('ok')

