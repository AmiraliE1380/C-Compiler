

class CodeGen:
    def __init__(self,compiler):
        self.curr_mem_address = 0
        self.curr_pb_address = 0 
        self.compiler = compiler
        self.bad_hash = {}
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
        
        elif action_symb == '#expr-id':
            addr = self.bad_hash[lookahead_token[1]]
            self.compiler.semantic_stack.append(addr)
        
        elif action_symb == '#B-assign':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2]
            self.compiler.program_block.append('(ASSIGN, ' + str(top) + ', '+ str(top1)+', )')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()

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
                self.compiler.program_block.append('(SUB, ' + str(top) +  ', ' +  str(top1) + ', ' +  str(t) + ')')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(t)

        elif action_symb == '#G-mult':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2]
            t = self.get_temp()
            self.compiler.program_block.append('(MULT, ' + str(top) +  ', '+ str(top1) +', ' + str(t) + ')')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(t)

        elif action_symb == '#factor-id':
            addr = self.bad_hash[lookahead_token[1]]
            self.compiler.semantic_stack.append(addr)
        
        elif action_symb == '#factor-num' or action_symb == '#factor-zeg-num': 
            self.compiler.semantic_stack.append('#'+ lookahead_token[1])

        elif action_symb == '#var-prime-ind':
            top = self.compiler.semantic_stack[-1]  # index
            top1 = self.compiler.semantic_stack[-2] # array
            mem_addr = top1 + 4*top
            t = self.get_temp()
            self.compiler.program_block.append('(ASSIGN, '+ str(mem_addr) + ', '+  str(t) + ', )')
            self.curr_pb_address += 1
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(t)

        elif action_symb == '#factor-prime-arg-begin':
            self.compiler.semantic_stack.append("@")
        
        elif action_symb =='#factor-prime-arg-end':
            args = []
            while self.compiler.semantic_stack[-1] != '@':
                args.append(self.compiler.semantic_stack[-1])
                self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            func_addr = self.compiler.semantic_stack[-1]
            if self.bad_hash['output'] == func_addr and len(args) == 1:
                self.compiler.program_block.append('(PRINT, '+ str(args[0]) + ', , )')
                self.curr_pb_address += 1

            
        


        print("Action " + action_symb + " is taken.")
        print('Lookahead token is : ', lookahead_token)
        for key,it in self.compiler.symbol_table.items():
            print(key, ' := ', it)
        print(self.compiler.semantic_stack)