


# checks if the variable is a non-terminal
def is_nonterminal(variable):
    return variable[0].isupper()

def syntax_error_terminal(terminal):
    if terminal == 'id':
        return 'ID'
    if terminal == 'num':
        return 'NUM'
    return terminal

# turn token into a terminal
def token_to_terminal(token):
    if token[0] == 'SYMBOL':
        return token[1]
    elif token[0] == 'ID':
        return 'id'
    elif token[0] == 'KEYWORD':
        return token[1]
    elif token[0] == 'NUM':
        return 'num'
    elif token[1] == '$':
        return '$'

def stringify_token(token):
    if token[1] == '$':
        return '$'
    return '('+token[0]+', '+token[1]+')'