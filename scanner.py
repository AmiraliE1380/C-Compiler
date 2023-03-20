tokens = []
errors = []
keywords = []
lexemes = []

all_symbols = [';', ':', ',', '[', ']', '(', ')', '=', '{', '}', '+', '-', '*', '<']
white_spaces = [' ', '\r', '\t', '\v', '\f']


def valid_chars_pre(char):
    if ('0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z' or
            char in all_symbols or char in white_spaces):
        return True
    return False


def clear(num, line):
    for _ in range(num):
        line.pop(0)


def is_NUM(line):
    if not '0' <= line[0] <= '9':
        return False

    number = ''
    for char in line:
        if '0' <= char <= '9':
            number += char
        else:
            if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                clear(len(number), line)
                while 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                    number += char
                    line.pop(0)
                    char = line[0]
                error(len(tokens), number, 'Invalid number')  # TODO:
                return True
            tokens[len(tokens) - 1].append(f'(NUM, {number})')
            clear(len(number), line)
            return True


def invalid_input(prev_str, line):
    line.pop(0)
    char = line[0]
    clear(len(prev_str), line)
    while not valid_chars_pre(char):
        prev_str += char
        line.pop(0)
        char = line[0]
    error(len(tokens), prev_str, 'Invalid input')


def is_ID_KEYWORD(line):
    if not ('a' <= line[0] <= 'z' or 'A' <= line[0] <= 'Z'):
        return False

    id = ''
    for char in line:
        if '0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            id += char
        else:
            if not valid_chars_pre(char):
                invalid_input(id + char, line)
                return True

            token = f'(ID, {id})'
            if (id == 'if' or id == 'else' or id == 'void' or id == 'int' or id == 'repeat' or
                    id == 'break' or id == 'until' or id == 'return'):
                token = f'(KEYWORD, {id})'
            elif id not in lexemes:
                lexemes.append(id)
            tokens[len(tokens) - 1].append(token)
            clear(len(id), line)
            return True


def is_SYMBOL(line):
    c = line[0]
    if line[0] == '=' and line[1] == '=':
        token = line[0] + line[1]
        clear_num = 2
    elif c in all_symbols:
        token = c
        clear_num = 1
    else:
        return False
    tokens[len(tokens) - 1].append(f'(SYMBOL, {token})')
    clear(clear_num, line)
    return True


def is_WHITESPACE(line):
    clear_count = 0
    for char in line:
        if char in white_spaces:
            clear_count += 1
        else:
            if clear_count == 0:
                return False
            break
    clear(clear_count, line)
    return True


def get_next_token(line):
    if is_WHITESPACE(line):
        return
    if is_NUM(line):
        return
    if is_ID_KEYWORD(line):
        return
    if is_SYMBOL(line):
        return

    invalid_input(line[0], line)


def write_errors():
    num_lines = len(tokens)
    output = ''
    for num_line in range(num_lines):
        line_has_errors = False
        for error in errors:
            if error[0] == num_line + 1:
                if not line_has_errors:
                    output += f'{num_line + 1}.\t'
                    line_has_errors = True
                output += f'({error[1]}, {error[2]}) '
        if line_has_errors:
            output += '\n'

    return output


def write_tokens():
    output = ''
    count = 0
    for line in tokens:
        count += 1
        if not line:
            continue
        output += f'{count}.\t'
        for token in line:
            output += f'{token} '
        output += '\n'

    return output


def write_symbols():
    output = f'''1.	break
2.	else
3.	if
4.	int
5.	repeat
6.	return
7.	until
8.	void'''
    for i in range(len(lexemes)):
        output += f'\n{i + 9}\t{lexemes[i]}'
    return output


def write_files():
    errors_file = open("lexical_errors.txt", "w")
    errors_file.write(write_errors())
    tokens_file = open("tokens.txt", "w")
    tokens_file.write(write_tokens())
    symbol_file = open("symbol_table.txt", "w")
    symbol_file.write(write_symbols())


def error(line_num, string, type):
    global errors
    errors.append((line_num, string, type))


def delete_comments(input_prog):
    comment = False
    comment_beg = None
    comment_count = 0
    line_num = 1
    for i in range(len(input_prog)):
        if not comment and input_prog[i] == '/' and i + 1 < len(input_prog) and input_prog[i + 1] == '*':
            comment = True
            comment_beg = i
        elif comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i + 1] == '/':
            comment = False
            for j in range(comment_beg, i + 2):
                input_prog[j] = -1  # deleting the comments
                comment_count += 1
        elif not comment and input_prog[i] == '*' and i + 1 < len(input_prog) and input_prog[i + 1] == '/':
            input_prog[i], input_prog[i + 1] = -1, -1
            comment_count += 2
            error(line_num, '*/', 'Unmatched comment')
        elif not comment and input_prog[i] == '\n':
            line_num += 1

    if comment:
        # maybe a bug is risen because of '/* comm...'
        error(line_num, '/* comm...', 'Unclosed comment')
        for j in range(comment_beg, len(input_prog)):
            input_prog[j] = -1  # deleting the comments
            comment_count += 1

    for _ in range(comment_count):
        input_prog.remove(-1)


def test(chars):
    prog = ''
    for char in chars:
        prog += char
    print(prog)


def get_lines(input_prog):
    delete_comments(input_prog)
    # test(input_prog)
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

    global tokens
    for line in lines:
        tokens.append([])
        while len(line) > 0:
            get_next_token(line)

    write_files()
