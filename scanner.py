tokens = []
errors = []
lexemes = []


def get_next_token(chars):
    pass


def write_files():
    pass


def scanner_run(input_prog):
    chars = list(input_prog)    # will produce list of characters
    print(chars)

    while len(chars) > 0:
        get_next_token(chars)

    write_files()
