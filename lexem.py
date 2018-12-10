import re
from copy import copy


class LexemAnalyser:


    keywords = 'if else while do begin end for switch case float double int byte char enum return break'.split()
    functions = 'sin cos tan tg ln'.split()
    opening_brackets = '[ } ('.split()
    closing_brackets = '] } )'.split()
    separators = '; ,'.split()
    operators = '* + - / %'.split()
    assignment_operators = ":=".split()
    comparators = "= <= >= <>".split()
    brackets_pairs = {
        "(": ")",
        "{": "}",
        "[": "]",
        ")": "(",
        "]": "[",
        "}": "{",
    }





    starts_with_char = re.compile(r'^¶*(?P<element>[a-zA-Z]?[a-zA-Z0-9]*)¶*(?P<left>.*)')
    starts_with_number = re.compile(r'^¶*(?P<element>\d*\.?\d*)¶*(?P<left>.*)')
    single_char = re.compile(r'^¶*(?P<element>^.)¶*(?P<left>.*)')
    double_char = re.compile(r'^¶*(?P<element>^..)¶*(?P<left>.*)')


    def __init__(self):
        exeptions = []

    def detect_lexems(self, phrase):
        lexems = []
        left = phrase.replace(" ", "¶").replace("\n", "¶").replace("\r", "¶")
        while left:
            element, left = self.starts_with_number.findall(left)[0]
            if element:
                lexems.append(Lexem(element, "NUMBER"))
                continue

            element, left = self.starts_with_char.findall(left)[0]
            if element:
                if element in self.keywords:
                    lexems.append(Lexem(element, "KEYWORD"))
                elif element in self.functions:
                    lexems.append(Lexem(element, "FUNCTION"))
                else:
                    lexems.append(Lexem(element, "VARIABLE"))
                continue



            element = left[:2]
            if element in self.comparators:
                lexems.append(Lexem(element, "COMPARATOR"))
                left = left[2:]
                continue
            elif element in self.operators:
                lexems.append(Lexem(element, "OPERATOR"))
                left = left[2:]
                continue
            elif element in self.assignment_operators:
                lexems.append(Lexem(element, "ASSIGNMENT_OPERATOR"))
                left = left[2:]
                continue

            element = left[:1]
            left = left[1:]
            if element in self.separators:
                lexems.append(Lexem(element, "SEPARATOR"))
            elif element in self.operators:
                lexems.append(Lexem(element, "OPERATOR"))
            elif element in self.assignment_operators:
                lexems.append(Lexem(element, "ASSIGNMENT_OPERATOR"))
            elif element in self.closing_brackets:
                lexems.append(Lexem(element, "CLOSING_BRACKET"))
            elif element in self.opening_brackets:
                lexems.append(Lexem(element, "OPENING_BRACKET"))
            else:
                lexems.append(Lexem(element, "UNKNOWN"))
        lexems = self.analyse_pairs(lexems)
        lexems = self.analyse_depth(lexems)
        return lexems

    def _lexem_is_bracket(self, lexem):
        return lexem.token in self.opening_brackets or lexem.token in self.closing_brackets

    def analyse_depth(self, lexems):
        # brackets = [
        #     (i, lexem) for i, lexem in enumerate(lexems)
        #     if lexem.token in self.opening_brackets or lexem.token in self.closing_brackets
        # ]
        depth = 0
        bracket_id = 0
        max_id = 0
        group_id_chain = [0]
        for i, lexem in enumerate(lexems):
            if lexem.token in self.opening_brackets:
                depth += 1
                bracket_id += 1
                max_id += 1
                group_id_chain.append(bracket_id)

            lexem.group_id_chain = copy(group_id_chain)

            if lexem.token in self.closing_brackets:
                depth -= 1
                group_id_chain.pop(-1)


        return lexems

    def analyse_pairs(self, lexems):
        for i, lexem in enumerate(lexems[:-1]):
            if lexems[i + 1].lexem_type in Lexem.next_available_lexem[lexem.lexem_type]:
                lexems[i + 1].status = "OK"
            elif lexem.token in Lexem.next_available_token.keys() and lexems[i + 1].lexem_type in \
                    Lexem.next_available_token[lexem.token]:
                lexems[i + 1].status = "OK"
            else:
                lexems[i + 1].status = "NOT OK"

                raise ExpressionSyntaxError(payload=(lexems, i + 1))
        return lexems

    def extract_bracket_groups(self, lexems):
        while True:
            max_depth = max(l.depth for l in lexems)
            if max_depth == 0:
                break

            group_id = -1
            lexems_new = list()
            for i, l in enumerate(lexems):
                if l.depth == max_depth:
                    group_changed = (l.group_id != group_id)
                    if group_changed:
                        lex_group = LexemGroup()
                        lex_group.group_id_chain = l.group_id_chain[:-1]
                        lexems_new.append(lex_group)
                        group_id = l.group_id

                    lex_group.lexems.append(l)
                else:
                    lexems_new.append(l)
            lexems = lexems_new
        lexem_group = LexemGroup(lexems=lexems)
        return lexem_group

class ExpressionSyntaxError(Exception):
    def __init__(self, payload=None, *args, **kwargs):
        lexems, i = payload
        left_part = " ".join([l.token for l in lexems[:i]])
        right_part = " ".join([l.token for l in lexems[i+1:]])
        message = ['Syntax error']
        message.append(f'{left_part} {lexems[i].token} {right_part}')
        message.append(f'{" " * len(left_part)} ^ invalid')
        super(ExpressionSyntaxError, self).__init__("\n".join(message))



class BaseLexem:
    available_lexem_types = "KEYWORD SEPARATOR OPERATOR NUMBER VARIABLE UNKNOWN ASSIGNMENT_OPERATOR COMPARATOR OPENING_BRACKET CLOSING_BRACKET".split()
    next_available_lexem = {
        "KEYWORD": "".split(),
        "SEPARATOR": "VARIABLE NUMBER KEYWORD CLOSING_BRACKET".split(),
        "OPERATOR": "NUMBER VARIABLE OPENING_BRACKET".split(),
        "NUMBER": "OPERATOR ASSIGNMENT_OPERATOR SEPARATOR CLOSING_BRACKET".split(),
        "VARIABLE": "COMPARATOR OPERATOR ASSIGNMENT_OPERATOR SEPARATOR CLOSING_BRACKET".split(),
        "COMPARATOR": "VARIABLE NUMBER".split(),
        "ASSIGNMENT_OPERATOR": "NUMBER VARIABLE FUNCTION OPENING_BRACKET".split(),
        "FUNCTION": "OPENING_BRACKET".split(),
        "UNKNOWN": "".split(),
        "OPENING_BRACKET": "NUMBER VARIABLE OPENING_BRACKET KEYWORD".split(),
        "CLOSING_BRACKET": "SEPARATOR CLOSING_BRACKET VARIABLE NUMBER OPENING_BRACKET KEYWORD OPERATOR".split(),
    }


    priorities = {}
    priorities.update({key: 1 for key in "+ - == != < >".split()})
    priorities.update({key: 2 for key in "* / %".split()})
    priorities.update({key: 3 for key in "= += -= /= *=".split()})

    next_available_token = {
        "if": "OPENING_BRACKET".split(),
        "else": "NUMBER VARIABLE".split(),

    }

    def __init__(self, token, lexem_type):
        self.token = token
        self.lexem_type =lexem_type
        self.status = ""
        self.group_id_chain = [0]

    @property
    def group_id(self):
        return self.group_id_chain[-1]


    @property
    def depth(self):
        return len(self.group_id_chain) - 1


    def __repr__(self):
        return f"{self.token}"




class LexemGroup(BaseLexem):
    def __init__(self, token=None, lexem_type='GROUP', lexems=None):
        super(LexemGroup, self).__init__(token, lexem_type)
        self.lexems = list() if not lexems else lexems
        self.lexem_type = lexem_type
        self.status = ""


    @property
    def token(self):
        return "_".join([l.token for l in self.lexems])

    @token.setter
    def token(self, value):
        pass


class KeywordLexem(BaseLexem):
    lexem_type = "KEYWORD"
    def __init__(self, *args, **kwargs):
        super(KeywordLexem, self).__init__(*args, **kwargs)

class SeparatorLexem(BaseLexem):
    lexem_type = "SEPARATOR"
    def __init__(self, *args, **kwargs):
        super(SeparatorLexem, self).__init__(*args, **kwargs)

class OperatorLexem(BaseLexem):
    lexem_type = "OPERATOR"
    def __init__(self, *args, **kwargs):
        super(OperatorLexem, self).__init__(*args, **kwargs)

class NumberLexem(BaseLexem):
    lexem_type = "NUMBER"
    def __init__(self, *args, **kwargs):
        super(NumberLexem, self).__init__(*args, **kwargs)

class VariableLexem(BaseLexem):
    lexem_type = "VARIABLE"
    def __init__(self, *args, **kwargs):
        super(VariableLexem, self).__init__(*args, **kwargs)

class ComparatorLexem(BaseLexem):
    lexem_type = "COMPARATOR"
    def __init__(self, *args, **kwargs):
        super(ComparatorLexem, self).__init__(*args, **kwargs)

class AssignmentOperatorLexem(BaseLexem):
    lexem_type = "ASSIGNMENTOPERATOR"
    def __init__(self, *args, **kwargs):
        super(AssignmentOperatorLexem, self).__init__(*args, **kwargs)

class FunctionLexem(BaseLexem):
    lexem_type = "FUNCTION"
    def __init__(self, *args, **kwargs):
        super(FunctionLexem, self).__init__(*args, **kwargs)

class UnknownLexem(BaseLexem):
    lexem_type = "UNKNOWN"
    def __init__(self, *args, **kwargs):
        super(UnknownLexem, self).__init__(*args, **kwargs)

class BracketLexem(BaseLexem):
    lexem_type = "BRACKET"
    def __init__(self, *args, **kwargs):
        super(BracketLexem, self).__init__(*args, **kwargs)

class OpeningBracketLexem(BracketLexem):
    lexem_type = "OPENINGBRACKET"
    def __init__(self, *args, **kwargs):
        super(OpeningBracketLexem, self).__init__(*args, **kwargs)


class ClosingBracketLexem(BracketLexem):
    lexem_type = "CLOSINGBRACKET"
    def __init__(self, *args, **kwargs):
        super(ClosingBracketLexem, self).__init__(*args, **kwargs)



lexem_classes = {
    "KEYWORD": KeywordLexem,
    "SEPARATOR": SeparatorLexem,
    "OPERATOR": OperatorLexem,
    "NUMBER": NumberLexem,
    "VARIABLE": VariableLexem,
    "COMPARATOR": ComparatorLexem,
    "ASSIGNMENT_OPERATOR": AssignmentOperatorLexem,
    "FUNCTION": FunctionLexem,
    "UNKNOWN": UnknownLexem,
    "OPENING_BRACKET": OpeningBracketLexem,
    "CLOSING_BRACKET": ClosingBracketLexem,
}

class Lexem(BaseLexem):
    def __new__(cls, token, lexem_type, *args, **kwargs):
        LexemClass = lexem_classes.get(lexem_type)
        return LexemClass(token, lexem_type, *args, **kwargs)