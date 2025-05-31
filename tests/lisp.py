from parser import *

g = Grammar() 

def digit_lexer(text, pos):
    i = pos
    value = ""
    while i < len(text) and text[i].isdigit():
        value += text[i]
        i += 1
    if i == pos:
        return (False, None, pos)
    return (
        True, 
        int(value),
        i
    )
g.define('number', Lexer(digit_lexer))


def identifier_lexer(text, pos):
    i = pos
    if i >= len(text) or not (text[i].isalpha() or text[i] == '_'):
        return (False, None, pos)
    value = text[i]
    i += 1
    while i < len(text) and (text[i].isalnum() or text[i] == '_'):
        value += text[i]
        i += 1
    return (True, value, i)
g.define('identifier', Lexer(identifier_lexer))


def operator_lexer(text, pos):
    operators = ['>=', '<=', '==', '!=', '&&', '||', '+', '-', '*', '/', '<', '>', '=']
    for op in sorted(operators, key=lambda x: -len(x)):
        if text.startswith(op, pos):
            return (True, op, pos + len(op))
    return (False, None, pos)
g.define('operator', Lexer(operator_lexer))

def space_lexer(text, pos):
    if text[pos] == ' ' or text[pos] == '\n':
        return (True, None, pos + 1)
    return (False, None, pos)
g.define('space', Lexer(space_lexer))

g.define('atom', Alt(
    Rule('number'),
    Rule('identifier'),
    Rule('operator'),
    Rule('space')
))

g.define('sexpr', Alt(
    Seq(
        Punc('('),
        Repeat(Rule('sexpr')),
        Punc(')')
    ),
    Rule('atom'),
))



tree = parse(g, "(12 + 12)", "sexpr")
print(json.dumps(tree, indent=2))

#tree2 = parse(g, "(define (square x) (* x x))", "sexpr")
#print(json.dumps(tree2, indent=2))
