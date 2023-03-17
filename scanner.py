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


def is_COMMENT(line):
    if not(line[0] == '/' and line[1] == '*'):
        return False
    clear_count = 2
    #while


def is_WHITESPACE(line):
    clear_count = 0
    for char in line:
        if char == ' ' or char == '\r' or char == '\t' or char == '\v' or char == '\f':
            clear_count +=1
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
    if is_COMMENT(line):
        return
    if is_NUM(line):
        return
    if is_ID(line):
        return
    if is_KEYWORD(line):
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
        elif comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i] == '/':
            comment = False
            for j in range(comment_beg, i):
                input_prog[j] = -1 # deleting the comments
                comment_count += 1
        elif not comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i] == '/':
            pass
            # TODO:Unmatched comment

    for _ in range(comment_count):
        input_prog.remove(-1)

    if comment:
        pass
        # TODO:unclosed comment


def get_lines(input_prog):
    delete_comments(input_prog)
    print(input_prog)
    print('hihihihi')
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
    #print(input_prog)
    lines = get_lines(list(input_prog))
    print(lines)
    for line in lines:
        while len(line) > 0:
            get_next_token(line)

    write_files()
