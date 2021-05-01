import lark
from lark import Lark, Transformer, v_args
import math
import random

variable = {'distance':0.0}

rule = open('map-grammer.lark').read()

parser = Lark(rule, parser='lalr', maybe_placeholders=True)

@v_args(inline=True)
class ParseMap(Transformer):
    from operator import sub, mul, truediv as div, mod
    #number = v_args(inline=True)(float)
    number = float

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

def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            print("Bye")
            break
        try:
            tree = parser.parse(s)
            #print(tree)
            print(tree.pretty())
            print(ParseMap().transform(tree))
        except Exception as other:
            print('incorrect input')
            print(other)
            continue
    
if __name__ == '__main__':
    # test()
    main()
