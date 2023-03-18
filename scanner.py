tokens = []
errors = []
lexemes = []


def clear(num, line):
    for _ in range(num):
        line.pop()


def is_NUM(line):
    if not '0' <= line[0] <= '9':
        return False

    number = ''
    for char in line:
        if '0' <= char <= '9':
            number += char
        else:
            tokens[len(tokens) - 1].append(f'(NUM, {number}) ')
            clear(len(number), line)
            return True


def is_ID_KEYWORD(line):
    if not ('a' <= line[0] <= 'z' or 'A' <= line[0] <= 'Z'):
        return False

    id = ''
    for char in line:
        if '0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            id += char
        else:
            token = f'(ID, {id}) '
            if id == 'if':
                token = '(KEYWORD, if) '
            if id == 'else':
                token = '(KEYWORD, else) '
            if id == 'void':
                token = '(KEYWORD, void) '
            if id == 'int':
                token = '(KEYWORD, int) '
            if id == 'repeat':
                token = '(KEYWORD, void) '
            if id == 'break':
                token = '(KEYWORD, break) '
            if id == 'until':
                token = '(KEYWORD, until) '
            if id == 'return':
                token = '(KEYWORD, return) '
            tokens[len(tokens) - 1].append(token)
            clear(len(id), line)
            return True


def is_SYMBOL(line):
    c = line[0]
    token = None
    if (c == ';' or c == ':' or c == ',' or c == '[' or c == ']' or c == '(' or c == ')'
            or c == '{' or c == '}' or c == '+' or c == '-' or c == '*' or c == '<'):
        token = c
        clear_num = 1
    if line[0] == '=' and line[1] == '=':
        token = line[0] + line[1]
        clear_num = 2
    if token is None:
        return False
    tokens[len(tokens) - 1].append(f'(SYMBOL, {token})')



def is_WHITESPACE(line):
    clear_count = 0
    for char in line:
        if char == ' ' or char == '\r' or char == '\t' or char == '\v' or char == '\f':
            clear_count += 1
        else:
            if clear_count == 0:
                return False
            break
    clear(clear_count, line)
    return True


def raise_error(chars):
    pass


def get_next_token(line):
    if is_WHITESPACE(line):
        return
    if is_NUM(line):
        return
    if is_ID_KEYWORD(line):
        return
    if is_SYMBOL(line):
        return

    raise_error(line)


def write_files():
    pass


def delete_comments(input_prog):
    comment = False
    comment_beg = None
    comment_count = 0
    for i in range(len(input_prog)):
        if not comment and input_prog[i] == '/' and i + 1 < len(input_prog) and input_prog[i + 1] == '*':
            comment = True
            comment_beg = i
        elif comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i + 1] == '/':
            comment = False
            for j in range(comment_beg, i + 2):
                input_prog[j] = -1  # deleting the comments
                comment_count += 1
        elif not comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i] == '/':
            pass
            # TODO:Unmatched comment

    for _ in range(comment_count):
        input_prog.remove(-1)

    if comment:
        pass
        # TODO:unclosed comment


def test(chars):
    prog = ''
    for char in chars:
        prog += char
    print(prog)


def get_lines(input_prog):
    delete_comments(input_prog)
    test(input_prog)
    print(input_prog)
    lines = []
    line = []
    for char in input_prog:
        if char == '\n':
            lines.append(line)
            line = []
        else:
            line.append(char)
    lines.append(line)
    return lines


def scanner_run(input_prog):
    lines = get_lines(list(input_prog))
    print(lines)
    for line in lines:
        tokens.append([])
        while len(line) > 0:
            get_next_token(line)

    write_files()
