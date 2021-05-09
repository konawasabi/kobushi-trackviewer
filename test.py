import lark
from lark import Lark, Transformer, v_args
import math
import random
import mapinterpleter as interp

rule = open('map-grammer.lark').read()

parser = Lark(rule, parser='lalr', maybe_placeholders=True)

def main():
    interpreter = interp.ParseMap(None,parser,prompt=True)
    while True:
        try:
            s = input('> ')
        except EOFError:
            print("Bye")
            break
        try:
            tree = parser.parse(s)
            print(tree)
            print(tree.pretty())
            #print(interpreter.transform(tree))
        except Exception as other:
            print('incorrect input')
            print(other)
            continue
    
if __name__ == '__main__':
    # test()
    main()
