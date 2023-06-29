

class CodeGen:
    def __init__(self,compiler):
        self.curr_mem_address = 0
        self.curr_pb_address = 0 
        self.compiler = compiler
        self.bad_hash = {}
        self.break_list = [] # tuples of (pb address of break, closest iteration scope)
        self.it_scope_list = [] # elements of label of scope
        self.define_output()


    def get_temp(self):
        self.compiler.memory.append(0)
        self.curr_mem_address += 4
        return self.curr_mem_address - 4
         
    
    def define_output(self):
        self.compiler.symbol_table[self.curr_mem_address] =  {'lexeme' : 'output', 'type': 'ID',
             'lineno' : -1, 'init_mem' : self.curr_mem_address ,'type': 'func', 'mem_size': 1}
        self.bad_hash['output'] =self.curr_mem_address
        self.curr_mem_address += 4

    def code_gen(self,action_symb):
        lookahead_token = self.compiler.lookahead_token
        if action_symb == '#decl-id':
            self.compiler.symbol_table[self.curr_mem_address] =  {'lexeme' : lookahead_token[1], 'type': lookahead_token[0],
             'lineno' : lookahead_token[2], 'init_mem' : self.curr_mem_address }
            self.bad_hash[lookahead_token[1]] =self.curr_mem_address


        elif action_symb == '#decl-var':
            self.compiler.symbol_table[self.curr_mem_address]['attr'] = {'type': 'var', 'mem_size': 1}
            self.compiler.memory.append(0)
            self.curr_mem_address += 4

        elif action_symb == '#decl-arr':
            self.compiler.symbol_table[self.curr_mem_address]['type'] =  {'type': 'var', 'mem_size': int(lookahead_token[1])}
            for _i in range(int(lookahead_token[1])):
                self.compiler.memory.append(0)
                self.curr_mem_address += 4
    
        elif action_symb == '#decl-func':
            self.compiler.symbol_table[self.curr_mem_address]['type'] =  {'type': 'func', 'mem_size': 1}
            self.compiler.memory.append(-1)
            self.curr_mem_address += 4

        elif action_symb == '#expr-stm-end':
            self.compiler.semantic_stack.pop()
        
        elif action_symb == '#expr-stm-break':
            self.break_list.append((self.curr_pb_address, self.it_scope_list[-1]))
            self.compiler.program_block.append(' ')
            self.curr_pb_address += 1
        
        elif action_symb == '#expr-id' or action_symb == '#factor-id':
            addr = self.bad_hash[lookahead_token[1]]
            self.compiler.semantic_stack.append(str(addr))
        
        elif action_symb == '#B-assign' or action_symb == '#H-assign':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2]
            self.compiler.program_block.append('(ASSIGN, ' + str(top) + ', '+ str(top1)+', )')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
        
        elif action_symb == '#B-expr-ind' or action_symb == '#var-prime-ind':
            top = self.compiler.semantic_stack[-1]  # index
            top1 = self.compiler.semantic_stack[-2] # array
            if top[0] == '#':
                mem_addr = int(top1) + 4*int(top[1:])
                self.compiler.semantic_stack.pop()
                self.compiler.semantic_stack.pop()
                self.compiler.semantic_stack.append(str(mem_addr))
            elif top[0] == '@':
                pass
            else:
                t = self.get_temp()
                s = self.get_temp()
                self.compiler.program_block.append('(MULT, ' + str(top) + ', '+ '#4, '+ str(s)+' )')
                self.compiler.program_block.append('(ADD, ' + str(s) + ', '+ '#' + str(top1)+', '+ str(t)+' )')
                self.curr_pb_address += 2
                self.compiler.semantic_stack.pop()
                self.compiler.semantic_stack.pop()
                self.compiler.semantic_stack.append('@'+ str(t))


        elif action_symb == '#D-addop':
            self.compiler.semantic_stack.append(lookahead_token[1])

        elif action_symb == '#D-add':
            top = self.compiler.semantic_stack[-1]
            op = self.compiler.semantic_stack[-2]
            top1 = self.compiler.semantic_stack[-3]
            t = self.get_temp()
            if op == '+':
                self.compiler.program_block.append('(ADD, ' + str(top) + ', ' + str(top1) + ', '+  str(t) +  ')')
            else:
                self.compiler.program_block.append('(SUB, ' + str(top1) +  ', ' +  str(top) + ', ' +  str(t) + ')')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(str(t))

        elif action_symb == '#G-mult':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2]
            t = self.get_temp()
            self.compiler.program_block.append('(MULT, ' + str(top) +  ', '+ str(top1) +', ' + str(t) + ')')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(t)
        
        elif action_symb == '#factor-num' or action_symb == '#factor-zeg-num': 
            self.compiler.semantic_stack.append('#'+ lookahead_token[1])

        elif action_symb == '#factor-prime-arg-begin':
            self.compiler.semantic_stack.append("@")
        
        elif action_symb =='#factor-prime-arg-end':
            args = []
            while self.compiler.semantic_stack[-1] != '@':
                args.append(self.compiler.semantic_stack[-1])
                self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            func_addr = int(self.compiler.semantic_stack[-1])
            if self.bad_hash['output'] == func_addr and len(args) == 1:
                self.compiler.program_block.append('(PRINT, '+ str(args[0]) + ', , )')
                self.curr_pb_address += 1

        elif action_symb == '#C-relop':
            self.compiler.semantic_stack.append(lookahead_token[1])
        
        elif action_symb == '#C-rel':
            top = self.compiler.semantic_stack[-1]
            op = self.compiler.semantic_stack[-2]
            top1 = self.compiler.semantic_stack[-3]
            t = self.get_temp()
            if op == '<':
                self.compiler.program_block.append('(LT, ' + str(top1) + ', ' + str(top) + ', '+  str(t) +  ')')
            else:
                self.compiler.program_block.append('(EQ, ' + str(top) +  ', ' +  str(top1) + ', ' +  str(t) + ')')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(t)

        elif action_symb == '#factor-expr'  or action_symb == '#factor-zeg-expr':
            pass

        elif action_symb == '#it-start':
            if len(self.it_scope_list) == 0:
                self.it_scope_list.append(0)
            else:
                self.it_scope_list.append(self.it_scope_list[-1] + 1)
            self.compiler.semantic_stack.append(str(self.curr_pb_address))

        elif action_symb == '#it-check':
            top = self.compiler.semantic_stack[-1] #expression value
            top1 = self.compiler.semantic_stack[-2] #iteration address
            self.compiler.program_block.append('(JPF, ' + str(top) +  ', '+ str(top1) + ', )')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            while len(self.break_list) > 0 and self.break_list[-1][1] == self.it_scope_list[-1]:
                self.compiler.program_block[self.break_list[-1][0]] = '(JP, '+str(self.curr_pb_address) + ', , )'
                self.break_list.pop()
            self.it_scope_list.pop()

            
        elif action_symb == '#sel-expr':
            self.compiler.program_block.append(' ')
            self.compiler.semantic_stack.append(str(self.curr_pb_address))
            self.curr_pb_address += 1

            
        elif action_symb == '#sel-endif':
            self.compiler.program_block.append(' ')
            self.compiler.semantic_stack.append(str(self.curr_pb_address))
            self.curr_pb_address += 1

        elif action_symb == '#sel-beginelse':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2] # begin if address
            top2 = self.compiler.semantic_stack[-3] # expression evaluation
            self.compiler.program_block[int(top1)] = ('(JPF, ' + str(top2) + ', ' + str(self.curr_pb_address) + ', )')
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(top)

        elif action_symb == '#sel-endelse':
            top = self.compiler.semantic_stack[-1]
            self.compiler.program_block[int(top)] = ('(JP, '  + str(self.curr_pb_address) + ', , )')
            self.compiler.semantic_stack.pop()



        # print("Action " + action_symb + " is taken.")
        # print('Lookahead token is : ', lookahead_token)
        # for key,it in self.compiler.symbol_table.items():
        #     print(key, ' := ', it)
        # print(self.compiler.semantic_stack)
        # print(self.compiler.program_block)