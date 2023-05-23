from anytree import Node, RenderTree
from scanner import Scanner
from grammar import Grammar
from token import is_nonterminal,syntax_error_terminal,token_to_terminal,stringify_token,is_action
from codegen import CodeGen

class Parser:
    def __init__(self,compiler):
        self.error_strings = []
        # the state of the parser is stored in a stack;  the rule, the index of the current transition, and the position in that transition
        self.state_stack = []
        self.compiler = compiler
        self.parent_node = Node('Program')




    def increment_state(self):
        current_state = self.state_stack[-1]
        current_state[2] += 1
        # check if the rule was completely matched
        while current_state[2] == len(self.compiler.grammar[current_state[0]][current_state[1]]):
            self.state_stack.pop()
            if len(self.state_stack) > 0:
                current_state = self.state_stack[-1]
                current_state[2]+=1
            else:
                break


    # matches the rules of the given nonterminal with the lookahead terminal
    def match_rule(self,nonterminal):
        if nonterminal not in self.compiler.grammar:
            # print('There is a mismatch in grammar')
            return
        epsilon_index = -1
        for transition_index in range(len(self.compiler.grammar[nonterminal])):
            first_index = 0
            while is_action( self.compiler.grammar[nonterminal][transition_index][first_index]):
                first_index += 1
            first_transition =  self.compiler.grammar[nonterminal][transition_index][first_index]
            
            if is_nonterminal(first_transition):
                if self.terminal_match_nonterminal(self.compiler.lookahead_terminal, first_transition):
                    return 1,transition_index, 'Nonterminal Matching'
                if self.terminal_match_nonterminal("epsilon", first_transition) and self.compiler.lookahead_terminal in self.compiler._grammer.follow_set(first_transition):
                    epsilon_index = transition_index
            else:
                if first_transition == 'epsilon' and self.compiler.lookahead_terminal in self.compiler._grammer.follow_set(nonterminal):
                    epsilon_index = transition_index
                elif self.compiler.lookahead_terminal == first_transition:
                    return 0, transition_index, 'Terminals Matching'
        if epsilon_index != -1:
            return 2,epsilon_index, 'Epsilon Matching'
        return 3,-1, 'Error: No Matching'

    # moves over the transitions of the DFA
    def run_dfa(self):
        while True:
            current_state = self.state_stack[-1]

            # find the rule that matches with the lookahead terminal
            if current_state[1] == -1:
                if len(self.compiler.grammar[current_state[0]]) > 1:
                    _, current_state[1], __ = self.match_rule(current_state[0])
                    if current_state[1] == -1:
                        return -1, 'Matching Failed'
                    current_state[2] = 0
                else:
                    current_state[1] = 0
                    current_state[2] = 0
            current_transition =  self.compiler.grammar[current_state[0]][current_state[1]][current_state[2]]
            print('Current Rule: ',current_state[0], current_transition)
            if is_action(current_transition):
                self.compiler.codegen.code_gen(current_transition)
                self.increment_state()
            elif is_nonterminal(current_transition):
                self.state_stack.append([current_transition,-1,-1,Node(current_transition,parent=current_state[3])])
                # elif 'epsilon' in first_set(current_transition) and lookahead_terminal in follow_set(current_transition):
                #     state_stack.append([current_transition,-1,-1,Node(current_transition,parent=current_state[3])])
                # else:
                #     return -1, 'Matching Failed'
            elif current_transition == 'epsilon':
                Node('epsilon',parent=current_state[3])
                self.increment_state()
                
            elif current_transition == self.compiler.lookahead_terminal:
                Node(stringify_token(self.compiler.lookahead_token),parent=current_state[3])
                self.increment_state()
                return 0,'Terminal Matching'
            else:
                return -2,'Missing a token'


    def panic_mode(self,result):
        lineno = self.compiler.lookahead_token[2]
        if result == -2:
            # missing a character
            missed_token = self.compiler.grammar[self.state_stack[-1][0]][self.state_stack[-1][1]][self.state_stack[-1][2]]
            self.error_strings.append('#'+str(lineno) +' : syntax error, missing '+ syntax_error_terminal(missed_token) + '\n')
            self.increment_state()
            return False
        elif result == -1:
            curr_var = self.state_stack[-1][0]
            if self.compiler.lookahead_terminal in self.compiler._grammer.follow_set(curr_var):
                self.error_strings.append('#'+str(lineno) +' : syntax error, missing '+ curr_var + '\n')
                self.state_stack[-1][3].parent = None
                self.state_stack.pop()
                self.increment_state()
                return False
            else:
                if self.compiler.lookahead_terminal != '$':
                    self.error_strings.append('#'+str(lineno) + ' : syntax error, illegal ' + syntax_error_terminal(self.compiler.lookahead_terminal) + '\n')
                    return True
                else:
                    self.error_strings.append('#'+str(lineno) + ' : syntax error, Unexpected EOF\n')
                    self.state_stack[-1][3].parent = None
                    return -1

    def write_errors(self):
        error_file = open('syntax_errors.txt',mode = 'w+', encoding='utf-8')
        if len(self.error_strings) == 0:
            error_file.write("There is no syntax error.")
        else:
            for _s in self.error_strings:
                error_file.write(_s)

    def write_parse_tree(self):
        parse_tree = open('parse_tree.txt', mode='w+', encoding='utf-8')
        all_nodes = [node for _,__,node in RenderTree(self.parent_node)]
        for pre, fill, node in RenderTree(self.parent_node):
            parse_tree.write('%s%s' % (pre, node.name))
            if node != all_nodes[-1]:
                parse_tree.write('\n')
        parse_tree.close()


    def write_codegen_output(self):
        output_file = open('output.txt', mode='w+', encoding='utf-8')
        for _i in range(len(self.compiler.program_block)):
            output_file.write(str(_i) +  '\t' +  self.compiler.program_block[_i]+ '\n')
        output_file.close()

    def parser_driver(self,input_prog):
        self.state_stack.append(['Program',-1,-1, self.parent_node])
        get_next_token = self.compiler.scanner.scanner(input_prog)
        get_new_token = True
        while len(self.state_stack) > 0:
            if get_new_token:
                self.compiler.lookahead_token = get_next_token()
                self.compiler.lookahead_terminal = token_to_terminal(self.compiler.lookahead_token)
            print('Current Terminal', self.compiler.lookahead_terminal)
            result,_=  self.run_dfa()   
            print(_)         
            if result == 0:
                # print(lookahead_token)
                # for pre, fill, node in RenderTree(parent_node):
                #     print('%s%s\n' % (pre, node.name))
                get_new_token = True
            if result != 0:
                get_new_token =  self.panic_mode(result)
                # for pre, fill, node in RenderTree(parent_node):
                #     print('%s%s\n' % (pre, node.name))
                # print(state_stack[-1])
                # print(error_strings[-1],end='')
                if get_new_token == -1:
                    break
            # input("")
        self.write_parse_tree()
        self.write_errors()
        self.write_codegen_output()

    # checks if a terminal is in the first set of the nonterminal
    def terminal_match_nonterminal(self,terminal,nonterminal):
        return terminal in self.compiler._grammer.first_set(nonterminal)