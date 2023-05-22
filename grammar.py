from token import is_nonterminal


class Grammar:
    def __init__(self):
        # NT s start with a capital letter and Terminals start with small letters.
        self.grammar = {
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
        self.terminals = ['id', 'num', ';', '[', ']', '(', ')', '{' , '}', 'void', 'int', 'if','else','break','repeat','until','return', '<', '==', '=','+','-','*',',','$']
        self.first_sets = {}
        self.follow_sets = {"Program": {'$'}}

    # calculates the first set of variable
    def first_set(self,variable):
        if not is_nonterminal(variable):
            return {variable}
        if variable in self.first_sets:
            return self.first_sets[variable]
        if variable not in self.grammar:
            return
        first = set()
        for rule in self.grammar[variable]:
            first = first | self.first_prod(rule)
        self.first_sets[variable] = first
        return first

    def first_prod(self,product):
        first = set()
        if len(product) == 0:
            return {'epsilon'}
        for term in product:
            term_first = self.first_set(term)
            first = first | term_first
            if 'epsilon' not in term_first:
                break
        return first

    # returns the follow set of the variable
    def follow_set(self,variable):
        if not is_nonterminal(variable):
            return 
        if variable not in self.grammar:
            return  
        if variable in self.follow_sets:
            return self.follow_sets[variable]  
        self.follow_set_init()
        return self.follow_sets[variable]   
        
    # calculates all the follow sets
    def follow_set_init(self):
        for vari in self.grammar:
            self.follow_sets[vari] = set()

        for vari in self.grammar:
            for rule in self.grammar[vari]:
                for term_ind in range(len(rule)):
                        if is_nonterminal(rule[term_ind]):
                            rest_product_first= self.first_prod(rule[term_ind+1:])
                            rest_product_first.discard('epsilon')
                            self.follow_sets[rule[term_ind]] = self.follow_sets[rule[term_ind]] | rest_product_first

        for vari in self.grammar:
            for rule in self.grammar[vari]:
                    if is_nonterminal(rule[-1]):
                        self.follow_sets[rule[-1]] = self.follow_sets[rule[-1]] | self.follow_sets[vari]

        for vari in self.grammar:
            for rule in self.grammar[vari]:
                for term_ind in range(len(rule)):
                        if is_nonterminal(rule[term_ind]):
                            rest_product_first= self.first_prod(rule[term_ind+1:])
                            if 'epsilon' in rest_product_first:
                                self.follow_sets[rule[term_ind]] = self.follow_sets[rule[term_ind]] | self.follow_sets[vari]