# розкриття дужок, конвейєр зі статичним тактом
from lexem import LexemAnalyser, LexemGroup
from syntax import SyntaxAnalyzer, BracketsOpener

from copy import copy





if __name__ == "__main__":
    qwe = '1 / (2 + 3) * 4 + (a + b) * (5 + (5 + 7 * (8  + 9))) - a'
    # qwe = '1 / (2 + 3) * 4 '
    # qwe = '1 + (2 - (3 + 4))'
    # qwe = '(1 + 2 ) * (4 - 5)'
    # qwe = input("input expression: ")
    lexem_analyzer = LexemAnalyser()
    lexems = lexem_analyzer.detect_lexems(qwe)

    lexem_group = lexem_analyzer.extract_bracket_groups(lexems)


    sa = SyntaxAnalyzer()
    syntax_tree = sa.parse_group(lexem_group)
    sa.print_tree(syntax_tree)

    # bo = BracketsOpener()
    # max_depth = bo.max_depth(syntax_tree)
    # print(max_depth)
    # opened = bo.open_brackets(syntax_tree)
    # syntax_tree_opened = sa.parse_list(opened)
    # sa.print_tree(syntax_tree_opened)



    print('ok')

