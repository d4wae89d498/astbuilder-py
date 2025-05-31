from parser import *

g = Grammar()
g.define_token('+', LEFT,   1)
g.define_token('-', LEFT,  1)
g.define_token('*', LEFT,   2)
g.define_token('/', LEFT,   2)
g.define_token('(', None,   0)

# 'macro' usage exemple bellow, with reccursive digit definition
#g.define('digit', Alt(*[Seq(Term(str(d))) for d in range(10)]))
#g.define('number', Alt(
#    Seq(Rule('digit'), Rule('number')),
#    Rule('digit')
#))
    #def flatify_digits(node):
#    ostr = ""
#    if isinstance(node["value"], dict):
#        return node["value"]["value"]
#    for item in node["value"]:
#        if isinstance(item, str):
#            ostr += item
#        else:
#            ostr += flatify_digits(item)
#    return ostr
#def int_macro(node):
#    node['value'] = flatify_digits(node)
#g.define_macro('number', int_macro)

# lexer based number definition
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


g.define('expr', Alt(
    Seq(Rule('expr'), Term('+'), Rule('expr')),
    Seq(Rule('expr'), Term('-'), Rule('expr')),
    Seq(Rule('expr'), Term('*'), Rule('expr')),
    Seq(Rule('expr'), Term('/'), Rule('expr')),
    Seq(Punc('('), Rule('expr'), Punc(')')),
    Rule('number'),
))

##############    

tree = parse(g, "5-2-1", "expr")
print(json.dumps(tree, indent=2))
print("=============")
tree = parse(g, "987", "expr")
print(json.dumps(tree, indent=2))