def number_lexer(text, pos):
    """Lexes integer constants (decimal, octal, hexadecimal)."""
    i = pos
    value = ""
    # Handle hexadecimal: 0[xX][0-9a-fA-F]+
    if i + 1 < len(text) and text[i] == '0' and text[i+1] in ('x', 'X'):
        value += text[i] + text[i+1]
        i += 2
        while i < len(text) and (text[i].isdigit() or text[i].lower() in 'abcdef'):
            value += text[i]
            i += 1
        return (True, int(value, 16), i)
    # Decimal or octal
    while i < len(text) and text[i].isdigit():
        value += text[i]
        i += 1
    if i == pos:
        return (False, None, pos)
    # By default treat as decimal (you could add octal detection if needed)
    return (True, int(value, 10), i)

def identifier_lexer(text, pos):
    """Lexes identifiers and keywords."""
    i = pos
    if i < len(text) and (text[i].isalpha() or text[i] == '_'):
        value = text[i]
        i += 1
        while i < len(text) and (text[i].isalnum() or text[i] == '_'):
            value += text[i]
            i += 1
        return (True, value, i)
    return (False, None, pos)

def string_literal_lexer(text, pos):
    """Lexes double-quoted string literals (no fancy escapes)."""
    if pos < len(text) and text[pos] == '"':
        i = pos + 1
        value = ""
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                # include escape and next character
                value += text[i] + text[i+1]
                i += 2
            elif text[i] == '"':
                i += 1
                return (True, value, i)
            else:
                value += text[i]
                i += 1
    return (False, None, pos)

def char_literal_lexer(text, pos):
    """Lexes single-quoted character constants (no fancy escapes)."""
    if pos < len(text) and text[pos] == "'":
        i = pos + 1
        value = ""
        if i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                value += text[i] + text[i+1]
                i += 2
            else:
                value += text[i]
                i += 1
            if i < len(text) and text[i] == "'":
                i += 1
                return (True, value, i)
    return (False, None, pos)

def float_lexer(text, pos):
    """
    Matches a simple floating‐point literal: digits '.' digits
    (no exponent, no leading '.', no suffix).
    Returns Python float.
    """
    i = pos
    digits_before = ""
    while i < len(text) and text[i].isdigit():
        digits_before += text[i]
        i += 1
    if i < len(text) and text[i] == '.':
        i += 1
        digits_after = ""
        while i < len(text) and text[i].isdigit():
            digits_after += text[i]
            i += 1
        if digits_before != "" or digits_after != "":
            value = float((digits_before or "0") + "." + (digits_after or "0"))
            return True, value, i
    return False, None, pos