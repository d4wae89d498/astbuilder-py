#   TODO:   Pratt identification/compilation shall be more flexible (checking seq length of 3 seems to weak)
#           Checker memo/backup/restore avec les ALT
#           Formalize output format
#           Add macro // functionnal parsers 
#           Standard way to ignore a comment/space

#           Standard standard language primitives

import json

# Define associativity constants
LEFT = 'LEFT'
RIGHT = 'RIGHT'

class Grammar:
    def __init__(self):
        self.tokens = {}
        self.rules = {}
        self.parsers = {}
        
        self.macros = []
        
    def define_token(self, token, associativity, precedence):
        self.tokens[token] = (associativity, precedence)
    
    def define_macro(self, rule, fn):
        self.macros.append((rule, fn))

    def define(self, name, combinator):
        self.rules[name] = combinator
        
    def compile(self):
        for name, combinator in self.rules.items():
            if self._is_pratt_rule(name, combinator):
                non_recursive, operators = self._extract_pratt(name, combinator)
                self.parsers[name] = PrattRule(non_recursive, operators)
            else:
                self.parsers[name] = combinator
                
    def _is_pratt_rule(self, rule_name, combinator):
        if not isinstance(combinator, Alt):
            return False
        has_binary = False
        has_non_recursive = False
        for alt in combinator.alts:
            if self._is_left_recursive_alt(rule_name, alt):
                if isinstance(alt, Seq) and len(alt.parsers) == 3:
                    a, b, c = alt.parsers
                    if (isinstance(a, Rule) and a.name == rule_name and
                        isinstance(b, Term) and
                        isinstance(c, Rule) and c.name == rule_name):
                        has_binary = True
            else:
                has_non_recursive = True
        return has_binary and has_non_recursive
    
    def _is_left_recursive_alt(self, rule_name, alt):
        if isinstance(alt, Seq) and alt.parsers:
            first = alt.parsers[0]
            return isinstance(first, Rule) and first.name == rule_name
        return False
    
    def _extract_pratt(self, rule_name, combinator):
        non_recursive = []
        operators = []
        for alt in combinator.alts:
            if (isinstance(alt, Seq) and len(alt.parsers) == 3):
                a, b, c = alt.parsers
                if (isinstance(a, Rule) and a.name == rule_name and
                    isinstance(b, Term) and
                    isinstance(c, Rule) and c.name == rule_name):
                    op = b.value
                    assoc, prec = self.tokens.get(op, (LEFT, 0))
                    operators.append((op, assoc, prec))
                    continue
            non_recursive.append(alt)


        alt = Alt(*non_recursive)
        alt.prat_name = rule_name
        
        return alt, operators

class Term:
    def __init__(self, value, skip = False):
        self.value = value
        self.skip = skip
    def parse(self, grammar, text, pos, memo):
        if text.startswith(self.value, pos):
            new_pos = pos + len(self.value)
            return (
                True, 
                {'type': 'Term', 'value': self.value} if not self.skip 
                else None, 
                new_pos
            )
        return (False, None, pos)
    
    def __repr__(self):
        return f"Term('{self.value}')"

class Lexer:
    def __init__(self, fn):
        self.fn = fn

    def parse(self, grammar, text, pos, memo):
        success, node, new_pos = self.fn(text, pos)
        if success:
            return (
                True, 
                node,
                new_pos
            )
        return (False, None, pos) 


class Punc(Term):
    def __init__(self, value, skip = True):
        self.value = value
        self.skip = skip
class Rule:
    def __init__(self, name):
        self.name = name
        
    def parse(self, grammar, text, pos, memo):
        key = (self.name, pos)
        if key in memo:
            return memo[key]
        
        # Mark as in-progress to prevent infinite recursion
        memo[key] = (False, None, pos)
        parser = grammar.parsers.get(self.name)
        if parser:
            success, tree, new_pos = parser.parse(grammar, text, pos, memo)
            if isinstance(tree,  dict) and "rule" in tree and tree["rule"] == self.name:
                node = tree
            elif tree is not None:
                node = {'rule': self.name, 'value': tree}
            else:
                node = None
            if success:
                memo[key] = (success, tree, new_pos)
                for on_rule,on_fn in grammar.macros:
                    if on_rule == self.name:
                        #print(on_rule)
                        on_fn(node)
            return (success, node, new_pos)
        return (False, None, pos)
    
    def __repr__(self):
        return f"Rule('{self.name}')"

class Seq:
    def __init__(self, *parsers):
        self.parsers = parsers
        
    def parse(self, grammar, text, pos, memo):
        current_pos = pos
        childrens = []
        for parser in self.parsers:
            success, tree, current_pos = parser.parse(grammar, text, current_pos, memo)
            if not success:
                return (False, None, pos)
            if tree:
                childrens.append(tree)
        return (True, childrens if len(childrens) > 1 else childrens[0], current_pos)
    
    def __repr__(self):
        return f"Seq({', '.join(map(repr, self.parsers))})"

class Alt:
    prat_name = None
    def __init__(self, *alts):
        self.alts = alts

    def parse(self, grammar, text, pos, memo):
        best_result = (False, None, pos)
        for expr in self.alts:
            success, node, new_pos = expr.parse(grammar, text, pos, memo)
            if success and new_pos > best_result[2]:
                best_result = (True, node, new_pos)
        if self.prat_name:
            tree =  best_result[1]      
            if isinstance(tree,  dict) and "rule" in tree and tree["rule"] == self.prat_name:
                node = tree
            else:
                node = {'rule': self.prat_name, 'value': node}
            best_result = (best_result[0], node, best_result[2])
        
        return best_result

    def __repr__(self):
        return f"Alt({', '.join(map(repr, self.alts))})"

class Macro:

    def __init__(self, rule, func):
        self.rule = rule
        self.func = func

    def parse(self, grammar, text, pos, memo):
        output = self.rule.parse(grammar, text, pos, memo)
        if output[0]:
            self.func(output[1])
        return output

class Repeat:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, grammar, text, pos, memo):
        current_pos = pos
        results = []
        while True:
            success, tree, new_pos = self.parser.parse(grammar, text, current_pos, memo)
            if not success or new_pos <= current_pos:
                break
            if tree is not None:
                results.append(tree)
            current_pos = new_pos
        return (True, results, current_pos)

    def __repr__(self):
        return f"Repeat({repr(self.parser)})"

class Opt:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, grammar, text, pos, memo):
        success, tree, new_pos = self.parser.parse(grammar, text, pos, memo)
        if success:
            return (True, tree, new_pos)
        else:
            return (True, None, pos)

    def __repr__(self):
        return f"Opt({repr(self.parser)})"


class PrattRule:
    def __init__(self, primary_parser, op_info_list):
        self.primary_parser = primary_parser
        self.op_info_list = op_info_list  # (op, associativity, precedence)
        
    def parse(self, grammar, text, pos, memo):
        return self._parse_pratt(grammar, text, pos, memo, 0)
    
    def _parse_pratt(self, grammar, text, pos, memo, min_precedence):

        success, left_tree, pos = self.primary_parser.parse(grammar, text, pos, memo)

        if not success:
            return (False, None, pos)
            
        while True:
            # Find all matching operators at current position
            possible_ops = []
            for op, assoc, prec in self.op_info_list:
                if prec < min_precedence:
                    continue
                op_len = len(op)
                if text.startswith(op, pos):
                    possible_ops.append((op, assoc, prec, op_len))
            
            if not possible_ops:
                break
                
            # Select highest precedence operator (with tie-breaker: longest match)
            possible_ops.sort(key=lambda x: (x[2], x[3]), reverse=True)
            chosen_op, assoc, prec, op_len = possible_ops[0]
            
            # Calculate next min precedence based on associativity
            next_min = prec + 1 if assoc == LEFT else prec
            
            # Advance past the operator
            op_pos = pos
            pos += op_len
            
            # Parse right operand
            success, right_tree, pos = self._parse_pratt(grammar, text, pos, memo, next_min)
            if not success:
                return (False, None, op_pos)


            # Combine into binary operation
            left_tree = {
                'rule': self.primary_parser.prat_name,
                'operator': chosen_op,
                'left': left_tree,
                'right': right_tree,
            }
            
        return (True, left_tree, pos)

def parse(grammar, text, start_rule='program'):
    grammar.compile()
    memo = {}
    parser = grammar.parsers[start_rule]
    success, tree, pos = parser.parse(grammar, text, 0, memo)
    if success and pos == len(text):
        return tree
    raise ValueError(f"Parse error at position {pos}")
