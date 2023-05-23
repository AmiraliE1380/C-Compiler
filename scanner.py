from token import untokenify


class Scanner:
    def __init__(self):
        self.tokens = []
        self.errors = []
        self.keywords = []
        self.lexemes = []

        self.all_symbols = [';', ':', ',', '[', ']', '(', ')', '=', '{', '}', '+', '-', '*', '<']
        self.white_spaces = [' ', '\r', '\t', '\v', '\f']

        
        self.all_lines = []
        self.lines_index = 0

    def is_valid_chars(self,char):
        if ('0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z' or
                char in self.all_symbols or char in self.white_spaces):
            return True
        return False


    def clear(self,num, line):
        for _ in range(num):
            line.pop(0)


    def is_NUM(self,line):
        if not '0' <= line[0] <= '9':
            return False

        number = ''
        for char in line:
            if '0' <= char <= '9':
                number += char
            else:
                if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                    number += char
                    self.clear(len(number), line)
                    self.error(len(self.tokens), number, 'Invalid number')
                    return True
                break
        self.tokens[len(self.tokens) - 1].append(f'(NUM, {number})')
        self.clear(len(number), line)
        return True


    def is_ID_KEYWORD(self,line):
        if not ('a' <= line[0] <= 'z' or 'A' <= line[0] <= 'Z'):
            return False

        id = ''
        for char in line:
            if '0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                id += char
            else:
                if not self.is_valid_chars(char):
                    id += char
                    self.error(len(self.tokens), id, 'Invalid input')
                    self.clear(len(id), line)
                    return True
                break

        token = f'(ID, {id})'
        if (id == 'if' or id == 'else' or id == 'void' or id == 'int' or id == 'repeat' or
                id == 'break' or id == 'until' or id == 'return'):
            token = f'(KEYWORD, {id})'
        elif id not in self.lexemes:
            self.lexemes.append(id)
        self.tokens[len(self.tokens) - 1].append(token)
        self.clear(len(id), line)
        return True


    def is_SYMBOL(self,line):
        c = line[0]
        if line[0] == '=' and line[1] == '=':
            token = line[0] + line[1]
            clear_num = 2
        elif c in self.all_symbols:
            token = c
            clear_num = 1
        else:
            return False
        if c not in [';', '[', ']'] and len(line) > 1 and line[1] != '/' and not self.is_valid_chars(line[1]):
            self.error(len(self.tokens), line[0] + line[1], 'Invalid input')
            line.pop(0)
            line.pop(0)
            return True
        self.tokens[len(self.tokens) - 1].append(f'(SYMBOL, {token})')
        self.clear(clear_num, line)
        return True


    def is_WHITESPACE(self,line):
        clear_count = 0
        for char in line:
            if char in self.white_spaces:
                clear_count += 1
            else:
                if clear_count == 0:
                    return False
                break
        self.clear(clear_count, line)
        return True


    def get_next_token(self,line):
        if self.is_WHITESPACE(line):
            return
        if self.is_NUM(line):
            return
        if self.is_ID_KEYWORD(line):
            return
        if self.is_SYMBOL(line):
            return

        if len(line) >= 2 and line[0] == '/' and line[1] != '/' and not self.is_valid_chars(line[1]):
            self.error(len(self.tokens), line[0] + line[1], 'Invalid input')
            line.pop(0)
            line.pop(0)
            return
        self.error(len(self.tokens), line[0], 'Invalid input')
        line.pop(0)


    def write_errors(self):
        if not self.errors:
            return 'There is no lexical error.'
        num_lines = len(self.tokens)
        output = ''
        for num_line in range(num_lines):
            line_has_errors = False
            for error in self.errors:
                if error[0] == num_line + 1:
                    if not line_has_errors:
                        output += f'{num_line + 1}.\t'
                        line_has_errors = True
                    output += f'({error[1]}, {error[2]}) '
            if line_has_errors:
                output += '\n'

        return output


    def write_tokens(self):
        output = ''
        count = 0
        for line in self.tokens:
            count += 1
            if not line:
                continue
            output += f'{count}.\t'
            for token in line:
                output += f'{token} '
            output += '\n'

        return output


    def write_symbols(self):
        output = f'''1.	break
2.	else
3.	if
4.	int
5.	repeat
6.	return
7.	until
8.	void'''
        for i in range(len(self.lexemes)):
            output += f'\n{i + 9}.\t{self.lexemes[i]}'
        return output


    def write_files(self):
        errors_file = open("lexical_errors.txt", "w")
        errors_file.write(self.write_errors())
        tokens_file = open("tokens.txt", "w")
        tokens_file.write(self.write_tokens())
        symbol_file = open("symbol_table.txt", "w")
        symbol_file.write(self.write_symbols())


    def error(self,line_num, string, type):
        self.errors.append((line_num, string, type))


    def delete_comments(self,input_prog):
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
                self.error(line_num, '*/', 'Unmatched comment')
            elif not comment and input_prog[i] == '\n':
                line_num += 1

        if comment:
            # maybe a bug is risen because of '/* comm...'
            self.error(line_num, '/* comm...', 'Unclosed comment')
            for j in range(comment_beg, len(input_prog)):
                input_prog[j] = -1  # deleting the comments
                comment_count += 1

        for _ in range(comment_count):
            input_prog.remove(-1)


    def get_lines(self,input_prog):
        self.delete_comments(input_prog)
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


    def scanner_run(self,input_prog):
        lines = self.get_lines(list(input_prog))
        for line in lines:
            self.tokens.append([])
            while len(line) > 0:
                self.get_next_token(line)

        self.write_files()

    def scanner(self,input_prog):
        self.all_lines = self.get_lines(list(input_prog))
        self.lines_index= 0
        def get_next_token_parse():
                self.tokens.append([])
                while len(self.tokens[-1]) == 0 and self.lines_index < len(self.all_lines):
                    if len(self.all_lines[self.lines_index]) > 0:
                        self.get_next_token(self.all_lines[self.lines_index])
                    else:
                        self.lines_index+= 1
                if len(self.tokens[-1]) != 0:
                    tok1,tok2 = untokenify(self.tokens[-1][0])
                    return tok1,tok2,self.lines_index+1
                return 'EOF', '$',self.lines_index
        return get_next_token_parse


def test(chars):
    prog = ''
    for char in chars:
        prog += char
    print(prog)