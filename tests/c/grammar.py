from parser import *
from tests.c.lexers import *

g = Grammar()


g.define_token("+", LEFT,  1)
g.define_token("-", LEFT,  1)
g.define_token("*", LEFT,  2)
g.define_token("/", LEFT,  2)
g.define_token("=", RIGHT,  0)

g.define("identifier",      Lexer(identifier_lexer))
g.define("int-literal",     Lexer(number_lexer))
g.define("float-literal",   Lexer(float_lexer))
g.define("char-literal",    Lexer(char_literal_lexer))

g.define("expr", Alt(
    Seq(Rule("expr"), Term("="), Rule("expr")),
    Seq(Rule("expr"), Term("+"), Rule("expr")),
    Seq(Rule("expr"), Term("-"), Rule("expr")),
    Seq(Rule("expr"), Term("*"), Rule("expr")),
    Seq(Rule("expr"), Term("/"), Rule("expr")),
    Alt(
        Seq(Punc("("), Rule("expr"), Punc(")")),
        Rule("identifier"),
        Rule("float-literal"),
        Rule("int-literal"),
        Rule("char-literal"),
    )
))

g.define("type-specifier", Alt(
    Term("int"),
    Term("float"),
    Term("char"),
))

g.define("decl-specifiers", Rule("type-specifier"))

g.define("declarator", Rule("identifier"))

g.define("initializer", Seq(
    Punc("="), Rule("expr")
))

g.define("init-declarator", Seq(
    Rule("declarator"),
    Opt(Rule("initializer"))
))

g.define("init-declarator-list", Seq(
    Rule("init-declarator"),
    Repeat(Seq(Punc(","), Rule("init-declarator"))),
))

g.define("declaration", Seq(
    Rule("decl-specifiers"),
    Rule("init-declarator-list"),
    Punc(";"),
))

g.define("return-stmt", Seq(
    Punc("return"),
    Opt(Rule("expr")),
    Punc(";"),
))

g.define("expr-stmt", Seq(
    Opt(Rule("expr")),
    Punc(";"),
))

g.define("statement", Alt(
    Rule("declaration"),
    Rule("return-stmt"),
    Rule("expr-stmt"),
    Rule("compound-stmt"),
))

g.define("compound-stmt", Seq(
    Punc("{"),
    Repeat(Rule("statement")),
    Punc("}"),
))

g.define("param-decl", Seq(
    Rule("type-specifier"),
    Rule("identifier"),
))

g.define("param-list", Seq(
    Rule("param-decl"),
    Repeat(Seq(Punc(","), Rule("param-decl"))),
))

g.define("function-declarator", Alt(
    Seq(Rule("identifier"), Punc("("), Rule("param-list"), Punc(")")),
    Seq(Rule("identifier"), Punc("("), Punc(")")),
))

g.define("function-definition", Seq(
    Rule("decl-specifiers"),
    Rule("function-declarator"),
    Rule("compound-stmt"),
))

g.define("external-declaration", Alt(
    Rule("function-definition"),
    Rule("declaration"),
))

g.define("translation-unit", Seq(
    Rule("external-declaration"),
    Repeat(Rule("external-declaration")),
))

if __name__ == "__main__":
    print("=== parse of expr ===")
    tree1 = parse(g, "42 +12.1", "expr")
    print(json.dumps(tree1, indent=2))

    src1 = """
    int x = 42 + 1.;
    """
    tree1 = parse(g, src1, "translation-unit")
    print("=== parse of global variable ===")
    print(json.dumps(tree1, indent=2))

    src2 = """int add(int a, int b) {
            int *k;
            int result;
            result = (a + b)-9-4-5;
            return result;
        }
            """
    tree2 = parse(g, src2, "translation-unit")
    print("\n=== parse of function add ===")
    print(json.dumps(tree2, indent=2))