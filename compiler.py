"""
Amirali Ebrahimzadeh - 98105546
Emad Zinoghli - 98103267
"""
from parser import Parser
from scanner import Scanner
from codegen import CodeGen
from grammar import Grammar
# address = "PA1_testcases\PA1_testcases\T10\input.txt"
# address = "P2_testcases\T09\input.txt"
# address = "TestCases_phase3\TestCases\T2\input.txt"
address = "TestCases_phase3/TestCases/T10/input.txt"
#address = 'input.txt'


class Compiler:
    def __init__(self):
        self.symbol_table = {}
        self.semantic_stack = []
        self.lookahead_terminal = ''
        self.lookahead_token = ('','')
        self._grammer = Grammar()
        self.grammar = self._grammer.grammar
        self.semantic_stack = []
        self.memory = []
        self.program_block = []
        self.scanner = Scanner()
        self.parser = Parser(self)
        self.codegen = CodeGen(self)

    def compile_parse(self,input_prog):
        self.parser.parser_driver(input_prog)

    def compile_scan(self,input_prog):
        self.scanner.scanner(input_prog)

input_prog = open(address, 'r').read()
Compiler().compile_parse(input_prog)