import getpass

from monkey import repl


def main():
    user = getpass.getuser()
    print('Hello {}! This is the Monkey programming language!'.format(user))
    print('Feel free to type in commands')
    repl.start()
