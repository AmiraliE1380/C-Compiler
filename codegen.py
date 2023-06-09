

class CodeGen:
    def __init__(self,compiler):
        self.curr_mem_address = 0
        self.curr_pb_address = 1
        self.compiler = compiler
        self.compiler.program_block = [' ']
        self.bad_hash = {}  # maps id of var or func to mem location
                            # Ex: bad_hash={'output': 0, 'fun': 4, 'zz': 8, 'x': 12, 'main': 20, 'a': 24, 'b': 28, 'c': 32}

        self.break_list = []  # tuples of (pb address of break, closest iteration scope)
        self.it_scope_list = []  # elements of label of scope
        self.define_output()

        self.latest_id = None
        self.current_func = 'main'
        self.func_arg_loc = None
        self.args_num = 0
        self.func_locations = {}
        self.func_return_addr = {}
        self.curr_decl_func = None
        self.funcs = []
        self.funcs_with_return = []
        self.call_seq_stack = ['main']

        self.count = 0


    def get_temp(self):
        self.compiler.memory.append(0)
        self.curr_mem_address += 4
        return self.curr_mem_address - 4
         
    
    def define_output(self):
        self.compiler.symbol_table[self.curr_mem_address] =  {'lexeme' : 'output', 'type': 'ID',
             'lineno' : -1, 'init_mem' : self.curr_mem_address ,'type': 'func', 'mem_size': 1}
        self.bad_hash['output'] =self.curr_mem_address
        self.curr_mem_address += 4


    def goto_func_loc(self):
        return_addr_saving_position = self.func_return_addr[self.current_func]
        self.compiler.program_block.append('(ASSIGN, #' +
                                           str(self.curr_pb_address+2) +  # plus 2 is to skip this and the next jump instruction
                                           ', ' + str(return_addr_saving_position) + ', )')
        self.compiler.program_block.append('(JP, #'+str(self.func_locations[self.current_func]) + ', , )')  # reconsider
        self.curr_pb_address += 2


    def handle_return_value(self):
        # print(f'self.func_has_return={self.funcs_with_return}')
        if self.current_func in self.funcs_with_return:
            return_val_addr = self.func_return_addr[self.current_func] - 4
            t = self.get_temp()
            print(f't={t}')
            self.compiler.program_block.append('(ASSIGN, ' + str(return_val_addr) + ', ' + str(t) + ', )')
            self.curr_pb_address += 1
            print(f'temp={t}')
            self.compiler.semantic_stack.append(t)


    def code_gen(self,action_symb):
        lookahead_token = self.compiler.lookahead_token

        print(f'{self.count}.\tss=\t{self.compiler.semantic_stack}\tlookahead={lookahead_token}\tbh=\t{self.bad_hash}\n')
        self.count += 1

        if action_symb == '#decl-id':
            self.compiler.symbol_table[self.curr_mem_address] =  {'lexeme' : lookahead_token[1], 'type': lookahead_token[0],
             'lineno' : lookahead_token[2], 'init_mem' : self.curr_mem_address }
            #print(f'lineno:{lookahead_token[2]}---lexeme:{lookahead_token[1]}')
            self.bad_hash[lookahead_token[1]] =self.curr_mem_address
            self.latest_id_decl = lookahead_token[1]


        elif action_symb == '#decl-var':
            self.compiler.symbol_table[self.curr_mem_address]['attr'] = {'type': 'var', 'mem_size': 1}
            self.compiler.memory.append(0)
            self.curr_mem_address += 4
            # print('hi')

        elif action_symb == '#decl-arr':
            self.compiler.symbol_table[self.curr_mem_address]['type'] =  {'type': 'var', 'mem_size': int(lookahead_token[1])}
            for _i in range(int(lookahead_token[1])):
                self.compiler.memory.append(0)
                self.curr_mem_address += 4
    

        elif action_symb == '#decl-func':
            self.compiler.symbol_table[self.curr_mem_address]['type'] = {'type': 'func', 'mem_size': 1}
            self.compiler.memory.append(-1)
            self.curr_mem_address += 4
            self.func_locations[self.latest_id_decl] = self.curr_pb_address
            self.curr_decl_func = self.latest_id_decl
            self.funcs.append(self.curr_decl_func)
            if self.curr_decl_func == 'main':
                jump_main_inst = '(JP, #' + str(self.curr_pb_address) + ', , )'
                self.compiler.program_block[0] = jump_main_inst

            #initiate self.break_list and self.it_scope_list
            self.break_list = []  # tuples of (pb address of break, closest iteration scope)
            self.it_scope_list = []  # elements of label of scope

            #print(f'func_locations={self.func_locations}')


        elif action_symb == '#expr-stm-end':
            self.compiler.semantic_stack.pop()
        
        elif action_symb == '#expr-stm-break':
            self.break_list.append((self.curr_pb_address, self.it_scope_list[-1]))
            self.compiler.program_block.append(' ')
            self.curr_pb_address += 1
        
        elif action_symb == '#expr-id' or action_symb == '#factor-id':
            addr = self.bad_hash[lookahead_token[1]]
            if not (lookahead_token[1] in self.funcs):
                #print(f'LA={lookahead_token[1]}')
                self.compiler.semantic_stack.append(str(addr))
        
        elif action_symb == '#B-assign' or action_symb == '#H-assign':
            top = self.compiler.semantic_stack[-1]
            top1 = self.compiler.semantic_stack[-2]
            self.compiler.program_block.append('(ASSIGN, ' + str(top) + ', '+ str(top1)+', )')
            print(f'{self.curr_pb_address}.\t{self.compiler.program_block[-1]}')
            print(f'ss={self.compiler.semantic_stack}')
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
            if not (lookahead_token[1] in self.funcs):
                #print(f'LA={lookahead_token[1]}')
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
        
        elif action_symb == '#factor-prime-arg-end':
            pass
            #print(f'semantic_stack={self.compiler.semantic_stack}')
            # args = []
            # while self.compiler.semantic_stack[-1] != '@':
            #     args.append(self.compiler.semantic_stack[-1])
            #     self.compiler.semantic_stack.pop()
            # print(f'args={args}')
            # #print(self.curr_mem_address)
            # self.compiler.semantic_stack.pop()
            # func_addr = int(self.compiler.semantic_stack[-1])
            # if self.bad_hash['output'] == func_addr and len(args) == 1:
            #     self.compiler.program_block.append('(PRINT, '+ str(args[0]) + ', , )')
            #     self.curr_pb_address += 1
            # #else:  # the call of other functions
                #print(f'bad_hash={self.bad_hash}')


        elif action_symb == '#C-relop':
            if not (lookahead_token[1] in self.funcs):
                #print(f'LA={lookahead_token[1]}')
                self.compiler.semantic_stack.append(lookahead_token[1])
        
        elif action_symb == '#C-rel':
            top = self.compiler.semantic_stack[-1]
            op = self.compiler.semantic_stack[-2]
            top1 = self.compiler.semantic_stack[-3]
            t = self.get_temp()
            if op == '<':
                self.compiler.program_block.append('(LT, ' + str(top1) + ', ' + str(top) + ', '+  str(t) +  ')')
                print('(LT, ' + str(top1) + ', ' + str(top) + ', '+  str(t) +  ')')
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
                print('(JP, ' + str(self.curr_pb_address) + ', , )')
                self.break_list.pop()
            print(self.compiler.program_block[-1])
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
            print('(JPF, ' + str(top) +  ', '+ str(top1) + ', )')
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.pop()
            self.compiler.semantic_stack.append(top)

        elif action_symb == '#sel-endelse':
            top = self.compiler.semantic_stack[-1]
            self.compiler.program_block[int(top)] = ('(JP, '  + str(self.curr_pb_address) + ', , )')
            print('(JP, '  + str(self.curr_pb_address) + ', , )')
            self.compiler.semantic_stack.pop()


        # phase 4 action symbols
        elif action_symb == '#latest-id':
            self.latest_id = lookahead_token[1]

        elif action_symb == '#call':
            self.current_func = self.latest_id
            self.call_seq_stack.append(self.current_func)
            self.func_arg_loc = self.bad_hash[self.current_func]
            self.args_num = 0
            #print(f'\ncurrent called function={self.current_func}')
            # print(f'semantic stack when call={self.compiler.semantic_stack}')
            # print(f'bad_hash={self.bad_hash}')

        elif action_symb == '#arg':
            self.args_num += 1
            #self.compiler.program_block.append('(ASSIGN, ' + str(top) + ', ' + str(top1) + ', )') #change this
            #print(f'arg mem loc = {self.curr_mem_address}')


        elif action_symb == '#end-call':
            args = []
            # print(f'ss={self.compiler.semantic_stack}')
            # print(f'args_num={self.args_num}')
            while self.args_num > 0:
                self.args_num -= 1
                args.append(self.compiler.semantic_stack[-1])
                self.compiler.semantic_stack.pop()
            if self.compiler.semantic_stack[-1] == '@':
                self.compiler.semantic_stack.pop()

            #print(f'args={args}')
            func_addr = int(self.compiler.semantic_stack[-1])
            if self.bad_hash['output'] == func_addr and len(args) == 1:
                self.compiler.program_block.append('(PRINT, ' + str(args[0]) + ', , )')
                self.curr_pb_address += 1
            else:
                args.reverse()
                for arg in args:
                    top = self.compiler.semantic_stack[-1]
                    self.func_arg_loc += 4
                    self.compiler.program_block.append('(ASSIGN, ' + str(arg) + ', ' + str(self.func_arg_loc) + ', )')
                    self.curr_pb_address += 1
                    #print(f'sssss={self.compiler.semantic_stack}')
                print(f'self.func_return_addr={self.func_return_addr}')
                self.goto_func_loc()
                self.handle_return_value()



        elif action_symb == '#save-return-loc':
            self.func_return_addr[self.curr_decl_func] = self.curr_mem_address
            print(f'self.func_return_addr={self.func_return_addr}')
            self.get_temp()




        elif action_symb == '#return-non-void':
            self.funcs_with_return.append(self.curr_decl_func)


        elif action_symb == '#return':
            #fix this!
            #print(f'\n\nself.call_seq_stack={self.call_seq_stack}\n\n')
            #print(self.func_return_addr[-1])
            #self.func_return_addr[self.call_seq_stack.pop()]

            if self.curr_decl_func != 'main':
                self.compiler.program_block.append('(JP, ' + str(self.curr_mem_address - 4) + ', , )')
                print('(JP, ' + str(self.curr_pb_address) + ', , )')
                self.compiler.semantic_stack.append(self.curr_mem_address)
                self.curr_pb_address += 1

            # self.compiler.program_block.append(self.curr_decl_func)
            # self.curr_pb_address += 1

        elif action_symb == '#return-num':
            # print('hiiiiiiiiiiiiiiii')
            if lookahead_token[0] == 'NUM':
                t = self.get_temp()
                self.compiler.program_block.append('(ASSIGN, #' + str(lookahead_token[1]) + ', ' + str(t) + ', )')
                self.curr_pb_address += 1
                #self.compiler.semantic_stack.append(t)

        # else:
        #     print('error')

        # print("Action " + action_symb + " is taken.")
        # print('Lookahead token is : ', lookahead_token)
        # for key,it in self.compiler.symbol_table.items():
        #     print(key, ' := ', it)
        # print(self.compiler.semantic_stack)
        # print(self.compiler.program_block)
