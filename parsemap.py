import lark
from lark import Lark, Transformer, v_args
import sys

import mapinterpleter as interp

if __name__ == '__main__':
    rule = open('map-grammer.lark').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    interpreter = interp.ParseMap(None,parser)
    
    argvs = sys.argv
    
    result = interpreter.load_files(argvs[1])
    
    print(result.own_track.data)
    
