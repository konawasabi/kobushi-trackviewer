from lark import Lark, Transformer, v_args
import math
import random

import mapobj

@v_args(inline=True)
class ParseMap(Transformer):
    from operator import sub, mul, truediv as div, mod
    
    number = float
    null_value = type(None)

    def __init__(self,env,prompt=False):
        self.promptmode = prompt
        if(env==None):
            self.environment = mapobj.Environment()
        else:
            self.environment = env
    def set_distance(self, value): #距離程設定
        self.environment.variable['distance'] = float(value)
    def call_distance(self): #距離程呼び出し
        return self.environment.variable['distance']
    def set_variable(self, *argument): #変数設定
        self.environment.variable[argument[0]]=argument[1]
    def call_variable(self, argument): #変数呼び出し
        return self.environment.variable[argument]
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
    def map_element(self, *argument):
        if(self.promptmode):
            a = 1
            for i in argument:
                if(i.data == 'mapobject'):
                    label = i.children[0]
                    key = i.children[1]
                    print('mapobject: label=',label,', key=',key)
                elif(i.data == 'mapfunc'):
                    label = i.children[0]
                    f_arg = i.children[1:]
                    print('mapfunc: label=',label,', args=',f_arg)
            print()
        else:
            first_obj = argument[0].children[0].lower()
            if(first_obj in ['curve','gradient']):
                temp = getattr(self.environment.own_track, first_obj)
                for elem in argument[1:]:
                    if(elem.data == 'mapfunc'):
                        break
                    temp = getattr(temp, elem.children[0].lower())
                getattr(temp, argument[-1].children[0].lower())(*argument[-1].children[1:])
    def start(self, *argument):
        if(all(elem == None for elem in argument)):
            return self.environment
