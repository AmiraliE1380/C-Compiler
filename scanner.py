tokens = []
errors = []
lexemes = []


def clear(num, line):
    for _ in range(num):
        line.pop()


def is_NUM(chars):
    pass


def is_ID(chars):
    pass


def is_KEYWORD(chars):
    pass


def is_SYMBOL(chars):
    pass


def is_COMMENT(chars):
    pass


def is_WHITESPACE(chars):
    pass


def get_next_token(chars):
    if is_WHITESPACE(chars):
        return
    if is_COMMENT(chars):
        return
    if is_NUM(chars):
        return
    if is_ID(chars):
        return
    if is_KEYWORD(chars):
        return
    if is_SYMBOL(chars):
        return




def write_files():
    pass


def get_lines(input_prog):
    lines = []
    line = []
    for char in input_prog:
        if char == '\n':
            lines.append(line)
            line = []
        else:
            line.append(char)
    return lines


def scanner_run(input_prog):
    lines = get_lines(list(input_prog))
    print(lines)
    for line in lines:
        while len(line) > 0:
            get_next_token(line)

    write_files()
