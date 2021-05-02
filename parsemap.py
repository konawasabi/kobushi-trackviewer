import lark
from lark import Lark, Transformer, v_args
import math
import random
import sys

head_str = 'BveTs Map '

class Environment():
    variable = {'distance':0.0}

@v_args(inline=True)
class ParseMap(Transformer):
    from operator import sub, mul, truediv as div, mod
    #number = v_args(inline=True)(float)
    number = float
    null_value = None

    #@v_args(inline=True)
    def set_distance(self, value): #距離程設定
        global variable
        #print(distance_g, value)
        variable['distance'] = float(value)
        return variable['distance']
    def call_distance(self): #距離程呼び出し
        global variable
        return variable['distance']
    def set_variable(self, *argument): #変数設定
        global variable
        variable[argument[0]]=argument[1]
    def call_variable(self, argument): #変数呼び出し
        global variable
        return variable[argument]
    def call_function(self, *argument): #数学関数呼び出し
        label = argument[0].lower()
        if (label == 'rand'):
            if(argument[1] == None): #引数なしrandかどうか
                return random.random()
            else:
                return random.uniform(0,argument[1])
        elif(label == 'abs'):
            return getattr(math,'fabs')(*argument[1:])
        else:
            return getattr(math,label)(*argument[1:])
    def remquote(self, value): #文字列からシングルクォート除去
        return value.replace("\'","")
    def add(self, *argument): #add演算子
        if(len(argument) == 2):
            if((type(argument[0]) == type(str()) and type(argument[1]) == type(str())) or (type(argument[0]) != type(str()) and type(argument[1]) != type(str()))):
                return argument[0]+argument[1]
            elif(type(argument[0]) == type(str())): # 引数が文字列&数値なら、数値を文字列に変換して結合。数値は整数に変換する。
                return argument[0]+str(int(argument[1]))
            else:
                return str(int(argument[0]))+argument[1]
        return 0
        
def load_map(path):
    f = open(argvs[1],'rb') #文字コードが不明なのでバイナリで読み込む
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
    
def parse_map(path, env):
    return None
    
def error_handle(er):
    print(er)
    return False

if __name__ == '__main__':
    rule = open('map-grammer.lark').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    e = Environment()
    
    argvs = sys.argv
    
    #print(load_map(argvs[1]))
    tree = parser.parse(load_map(argvs[1]), on_error=error_handle)
    print(tree.pretty())
