from monkey import lexer, parser, token

PROMPT = '>> '


def start():
    while True:
        line = input(PROMPT)
        if not line:
            return

        l = lexer.Lexer(line)
        p = parser.Parser(l)

        program = p.parse_program()
        if len(p.errors) != 0:
            print_parse_errors(p.errors)
            continue

        print(program.string())


MONKEY_FACE = r'''            __,__
   .--.  .-"     "-.  .--.
  / .. \/  .-. .-.  \/ .. \
 | |  '|  /   Y   \  |'  | |
 | \   \  \ 0 | 0 /  /   / |
  \ '- ,\.-"""""""-./, -' /
   ''-' /_   ^ ^   _\ '-''
       |  \._   _./  |
       \   \ '~' /   /
        '._ '-=-' _.'
           '-----'
'''


def print_parse_errors(errors):
    print(MONKEY_FACE)
    print('Woops! We ran into some monkey business here!')
    print(' parser errors:')
    for msg in errors:
        print('\t' + msg)
