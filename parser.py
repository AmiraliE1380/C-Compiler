from anytree import Node, RenderTree
import scanner

# NT s start with a capital letter and Terminals start with small letters.
Grammar = {
    'Program': [['Declaration-list','$']],
    'Declaration-list': [['Declaration', 'Declaration-list'], ['epsilon']],
    'Declaration': [['Declaration-initial', 'Declaration-prime']],
    'Declaration-initial': [['Type-specifier','id']],
    'Declaration-prime': [['Fun-declaration-prime'], ['Var-declaration-prime']],
    'Var-declaration-prime': [[';'], ['[', 'num', ']', ';']],
    'Fun-declaration-prime': [['(', 'Params', ')', 'Compound-stmt']],
    'Type-specifier': [['int'], ['void']],
    'Params': [['int', 'id', 'Param-prime', 'Param-list'], ['void']],
    'Param-list': [[',', 'Param', 'Param-list'], ['epsilon']],
    'Param': [['Declaration-initial', 'Param-prime']],
    'Param-prime': [['[', ']'],['epsilon']],
    'Compound-stmt': [['{', 'Declaration-list', 'Statement-list', '}']],
    'Statement-list': [['Statement', 'Statement-list'], ['epsilon']],
    'Statement': [['Expression-stmt'], ['Compound-stmt'], ['Selection-stmt'], ['Iteration-stmt'], ['Return-stmt']],
    'Expression-stmt': [['Expression', ';'], ['break', ';'], ';'],
    'Selection-stmt': [['if', '(', 'Expression', ')', 'Statement', 'else', 'Statement']],
    'Iteration-stmt': [['repeat', 'Statement', 'until', '(', 'Expression',')']],
    'Return-stmt': [['return', 'Return-stmt-prime']],
    'Return-stmt-prime': [[';'], ['Expression', ';']],
    'Expression': [['Simple-expression-zegond'], ['id', 'B']],
    'B': [['=','Expression'], ['[', 'Expression', ']', 'H'], ['Simple-expression-prime']],
    'H': [['=', 'Expression'], ['G', 'D','C']],
    'Simple-expression-zegond':[['Additive-expression-zegond', 'C']],
    'Simple-expression-prime':[['Additive-expression-prime','C']],
    'C' :[['Relop', 'Additive-expression'], ['epsilon']],
    'Relop':[['<'], ['==']],
    'Additive-expression': [['Term', 'D']],
    'Additive-expression-prime': [['Term-prime', 'D']],
    'Additive-expression-zegond': [['Term-zegond', 'D']],
    'D': [['Addop','Term', 'D'], ['epsilon']],
    'Addop': [['+'], ['-']],
    'Term': [['Factor', 'G']],
    'Term-prime': [['Factor-prime', 'G']],
    'Term-zegond': [['Factor-zegond', 'G']],
    'G': [['*', 'Factor', 'G'], ['epsilon']],
    'Factor': [['(', 'Expression', ')'], ['id', 'Var-call-prime'], ['num']],
    'Var-call-prime': [['(', 'Args', ')'], ['Var-prime']],
    'Var-prime': [['[', 'Expression', ']'], ['epsilon']],
    'Factor-prime':[['(', 'Args', ')'], ['epsilon']],
    'Factor-zegond':[['(', 'Expression', ')'], ['num']],
    'Args': [['Arg-list'], ['epsilon']],
    'Arg-list':[['Expression', 'Arg-list-prime']],
    'Arg-list-prime':[[',', 'Expression', 'Arg-list-prime'], ['epsilon']]
}
Terminals = ['id', 'num', ';', '[', ']', '(', ')', '{' , '}', 'void', 'int', 'if','else','break','repeat','until','return', '<', '==', '=','+','-','*',',','$']
First_set = {}
Follow_set = {"Program": {'$'}}
error_strings = []
# the state of the parser is stored in a stack;  the rule, the index of the current transition, and the position in that transition
state_stack = []
lookahead_terminal = ''
lookahead_token = ('','')

# checks if the variable is a non-terminal
def is_nonterminal(variable):
    return variable[0].isupper()

# calculates the first set of variable
def first_set(variable):
    if not is_nonterminal(variable):
        return {variable}
    if variable in First_set:
        return First_set[variable]
    if variable not in Grammar:
        return
    first = set()
    for rule in Grammar[variable]:
        first = first | first_prod(rule)
    First_set[variable] = first
    return first

def first_prod(product):
    first = set()
    if len(product) == 0:
        return {'epsilon'}
    for term in product:
        term_first = first_set(term)
        first = first | term_first
        if 'epsilon' not in term_first:
            break
    return first

# calculates the follow set of variable
def follow_set(variable):
    if not is_nonterminal(variable):
        return 
    if variable not in Grammar:
        return  
    if variable in Follow_set:
        return Follow_set[variable]     
    for vari in Grammar:
        Follow_set[vari] = set()

    for vari in Grammar:
        for rule in Grammar[vari]:
            for term_ind in range(len(rule)):
                    if is_nonterminal(rule[term_ind]):
                        rest_product_first= first_prod(rule[term_ind+1:])
                        rest_product_first.discard('epsilon')
                        Follow_set[rule[term_ind]] = Follow_set[rule[term_ind]] | rest_product_first

    for vari in Grammar:
        for rule in Grammar[vari]:
                if is_nonterminal(rule[-1]):
                    Follow_set[rule[-1]] = Follow_set[rule[-1]] | Follow_set[vari]

    for vari in Grammar:
        for rule in Grammar[vari]:
            for term_ind in range(len(rule)):
                    if is_nonterminal(rule[term_ind]):
                        rest_product_first= first_prod(rule[term_ind+1:])
                        if 'epsilon' in rest_product_first:
                            Follow_set[rule[term_ind]] = Follow_set[rule[term_ind]] | Follow_set[vari]
    return Follow_set[variable]


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


# checks if a terminal is in the first set of the nonterminal
def terminal_match_nonterminal(terminal,nonterminal):
    return terminal in first_set(nonterminal)


def increment_state():
    current_state = state_stack[-1]
    current_state[2] += 1
    # check if the rule was completely matched
    while current_state[2] == len(Grammar[current_state[0]][current_state[1]]):
        state_stack.pop()
        if len(state_stack) > 0:
            current_state = state_stack[-1]
            current_state[2]+=1
        else:
            break


# matches the rules of the given nonterminal with the lookahead terminal
def match_rule(nonterminal):
    if nonterminal not in Grammar:
        # print('There is a mismatch in grammar')
        return
    epsilon_index = -1
    for transition_index in range(len(Grammar[nonterminal])):
        first_transition = Grammar[nonterminal][transition_index][0] 
        if is_nonterminal(first_transition):
            if terminal_match_nonterminal(lookahead_terminal, first_transition):
                return 1,transition_index, 'Nonterminal Matching'
            if terminal_match_nonterminal("epsilon", first_transition) and lookahead_terminal in follow_set(first_transition):
                epsilon_index = transition_index
        else:
            if first_transition == 'epsilon' and lookahead_terminal in follow_set(nonterminal):
                epsilon_index = transition_index
            elif lookahead_terminal == first_transition:
                return 0, transition_index, 'Terminals Matching'
    if epsilon_index != -1:
        return 2,epsilon_index, 'Epsilon Matching'
    return 3,-1, 'Error: No Matching'

# moves over the transitions of the DFA
def run_dfa():
    while True:
        current_state = state_stack[-1]

        # find the rule that matches with the lookahead terminal
        if current_state[1] == -1:
            if len(Grammar[current_state[0]]) > 1:
                _, current_state[1], __ = match_rule(current_state[0])
                if current_state[1] == -1:
                    return -1, 'Matching Failed'
                current_state[2] = 0
            else:
                current_state[1] = 0
                current_state[2] = 0
        current_transition =  Grammar[current_state[0]][current_state[1]][current_state[2]]
        # print('Current Rule: ',current_state[0], current_transition)
        if is_nonterminal(current_transition):
            state_stack.append([current_transition,-1,-1,Node(current_transition,parent=current_state[3])])
            # elif 'epsilon' in first_set(current_transition) and lookahead_terminal in follow_set(current_transition):
            #     state_stack.append([current_transition,-1,-1,Node(current_transition,parent=current_state[3])])
            # else:
            #     return -1, 'Matching Failed'
        elif current_transition == 'epsilon':
            Node('epsilon',parent=current_state[3])
            increment_state()
            
        elif current_transition == lookahead_terminal:
            Node(stringify_token(lookahead_token),parent=current_state[3])
            increment_state()
            return 0,'Terminal Matching'
        else:
            return -2,'Missing a token'
            

def syntax_error_terminal(terminal):
    if terminal == 'id':
        return 'ID'
    if terminal == 'num':
        return 'NUM'
    return terminal


def panic_mode(result,lineno):
    if result == -2:
        # missing a character
        missed_token = Grammar[state_stack[-1][0]][state_stack[-1][1]][state_stack[-1][2]]
        error_strings.append('#'+str(lineno) +' : syntax error, missing '+ syntax_error_terminal(missed_token) + '\n')
        increment_state()
        return False
    elif result == -1:
        curr_var = state_stack[-1][0]
        if lookahead_terminal in follow_set(curr_var):
            error_strings.append('#'+str(lineno) +' : syntax error, missing '+ curr_var + '\n')
            state_stack[-1][3].parent = None
            state_stack.pop()
            increment_state()
            return False
        else:
            if lookahead_terminal != '$':
                error_strings.append('#'+str(lineno) + ' : syntax error, illegal ' + syntax_error_terminal(lookahead_terminal) + '\n')
                return True
            else:
                error_strings.append('#'+str(lineno) + ' : syntax error, Unexpected EOF\n')
                state_stack[-1][3].parent = None
                return -1

def write_errors():
    error_file = open('syntax_errors.txt',mode = 'w+', encoding='utf-8')
    if len(error_strings) == 0:
        error_file.write("There is no syntax error.")
    else:
        for _s in error_strings:
            error_file.write(_s)

def write_parse_tree(parent_node):
    parse_tree = open('parse_tree.txt', mode='w+', encoding='utf-8')
    all_nodes = [node for _,__,node in RenderTree(parent_node)]
    for pre, fill, node in RenderTree(parent_node):
        parse_tree.write('%s%s' % (pre, node.name))
        if node != all_nodes[-1]:
            parse_tree.write('\n')
    parse_tree.close()

def parser_driver(input_prog):
    parent_node = Node('Program')
    state_stack.append(['Program',-1,-1, parent_node])
    get_next_token = scanner.scanner(input_prog)
    get_new_token = True
    while len(state_stack) > 0:
        global lookahead_terminal
        global lookahead_token
        if get_new_token:
            lookahead_token = get_next_token()
            lookahead_terminal = token_to_terminal(lookahead_token)
        # print('Current Terminal', lookahead_terminal)
        result,_=  run_dfa()            
        if result == 0:
            # print(lookahead_token)
            # for pre, fill, node in RenderTree(parent_node):
            #     print('%s%s\n' % (pre, node.name))
            get_new_token = True
        if result != 0:
            get_new_token =  panic_mode(result,lookahead_token[2])
            # for pre, fill, node in RenderTree(parent_node):
            #     print('%s%s\n' % (pre, node.name))
            # print(state_stack[-1])
            # print(error_strings[-1],end='')
            if get_new_token == -1:
                break
        # input("")
    write_parse_tree(parent_node)
    write_errors()

