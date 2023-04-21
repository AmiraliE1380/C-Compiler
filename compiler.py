"""
Amirali Ebrahimzadeh - 98105546
Emad Zinoghli - 98103267
"""

import parser

address = "input.txt"

input_prog = open(address, 'r').read()
parser.parser_driver(input_prog)