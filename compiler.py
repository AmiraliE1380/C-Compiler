"""
Amirali Ebrahimzadeh - 98105546
Emad Zinoghli - 98103267
"""
from parser import Parser

address = "P2_testcases\T09\input.txt"

input_prog = open(address, 'r').read()
Parser().parser_driver(input_prog)