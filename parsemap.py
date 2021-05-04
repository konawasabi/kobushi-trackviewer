import lark
from lark import Lark, Transformer, v_args
import math
import random
import sys

import mapinterpleter as interp

head_str = 'BveTs Map '
        
def load_map(path):
    f = open(path,'rb') #文字コードが不明なのでバイナリで読み込む
    header = f.readline().decode('utf-8') #一行目をutf-8でデコード。日本語コメントが一行目にあると詰む
    f.close()

    #print(repr(header))
    data = ''

    ix = header.find(head_str)
    #print(ix)
    if(ix>=0):
        #print(header[ix:ix+len(head_str)])
        header_directive = header[ix+len(head_str):-1]
        #print(header_directive)
        if(':' in header_directive):
            header_version = float(header_directive.split(':')[0])
            header_encoding = header_directive.split(':')[1]
            #print('map version: ',header_version,', map encoding: ',header_encoding)
        else:
            header_version = float(header_directive)
            header_encoding = 'utf-8'
            #print('map version: ',header_version,', map encoding: ',header_encoding)
        if(header_version < 2):
            print('incompatible map version')
        else:
            f = open(argvs[1],'r',encoding=header_encoding)
            f.readline()
            data = f.read()
            f.close()
    else:
        print('header error')
    #print(f.read())
    return data
    
def error_handle(er):
    print(er)
    return False

if __name__ == '__main__':
    rule = open('map-grammer.lark').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    interpreter = interp.ParseMap(None)
    
    argvs = sys.argv
    
    tree = parser.parse(load_map(argvs[1]), on_error=error_handle)
    result = interpreter.transform(tree)
    
    print(result.own_track.data)
    
