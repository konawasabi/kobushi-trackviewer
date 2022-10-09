'''
    Copyright 2021-2022 konawasabi

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from lark import Lark, Transformer, v_args, exceptions
import math
import random
import os

from . import loadheader
from . import mapobj
from . import loadmapgrammer

@v_args(inline=True)
class ParseMap(Transformer):
    from operator import sub, mul, mod, neg, pos
    
    number = float
    null_value = type(None)

    def __init__(self,env,parser,prompt=False):
        self.promptmode = prompt
        
        grammer_fp = loadmapgrammer.loadmapgrammer()
        self.parser = Lark(grammer_fp.read(), parser='lalr', maybe_placeholders=True) if parser == None else parser
        grammer_fp.close()
        
        if(env==None):
            self.environment = mapobj.Environment()
            self.isroot=True
        else:
            self.environment = env
            self.isroot=False
    def set_distance(self, value): #距離程設定
        self.environment.variable['distance'] = float(value)
        self.environment.controlpoints.add(float(value))
    def call_predefined_variable(self, argument): #規定変数呼び出し（現実的にはdistanceのみ）
        return self.environment.variable[argument.lower()]
    def set_variable(self, *argument): #変数設定
        self.environment.variable[argument[0].lower()]=argument[1]
    def call_variable(self, argument): #変数呼び出し
        return self.environment.variable[argument.lower()]
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
    def div(self, *argument): #div演算子
        if(len(argument) == 2):
            return argument[0] / argument[1] if argument[1] != 0 else math.copysign(math.inf,argument[0])
        return 0
    def map_element(self, *argument): #マップ要素
        #import pdb
        #pdb.set_trace()
        if(self.promptmode): #プロンプトモード（テスト時のみ使用）のとき、マップ要素の構文解析だけ行う
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
            first_obj = argument[0].children[0].lower() # 先頭のマップ要素名を抽出して小文字に変換
            if(first_obj in ['curve','gradient','legacy']): # 自軌道に関係する要素か？
                temp = getattr(self.environment.own_track, first_obj) # 対応するオブジェクトを取得する
                for elem in argument[1:]: # 2番目以降もマップ要素かどうか(例: Track.X.Interpolate(...) or Track.Position(...) )
                    if(elem.data == 'mapfunc'): # 関数なら探索中止
                        break
                    temp = getattr(temp, elem.children[0].lower()) # 対応するオブジェクトを取得
                getattr(temp, argument[-1].children[0].lower())(*argument[-1].children[1:]) # 対応するマップ関数を呼び出す
            elif(first_obj in ['station']): # station要素
                key = argument[0].children[1] # stationKeyを取得
                temp = getattr(self.environment, first_obj) # stationオブジェクトを取得
                for elem in argument[1:]: # 子要素があるかどうか？
                    if(elem.data == 'mapfunc'):
                        break
                    temp = getattr(temp, elem.children[0].lower())
                if(key == None): # マップ関数に渡す引数を設定
                    temp_argv=argument[-1].children[1:] # stationKeyが指定されていない場合、マップファイルで指定された引数をそのまま渡す
                else:
                    temp_argv = [key] # stationKeyがある場合、マップファイル指定の引数の先頭にkeyを追加する
                    temp_argv.extend(argument[-1].children[1:])
                getattr(temp, argument[-1].children[0].lower())(*temp_argv)
            elif(first_obj in ['track']):
                key = argument[0].children[1] # trackKeyを取得
                temp_argv = [key] # マップファイル指定の引数の先頭にkeyを追加する
                temp_argv.extend(argument[-1].children[1:])
                temp = getattr(self.environment, 'othertrack') # othertrackオブジェクトを取得する
                if(argument[1].children[0].lower() == 'cant' and argument[1].data == 'mapfunc'): # Track[key].Cant(x)かどうか
                    temp = getattr(temp, 'cant')
                    getattr(temp, 'interpolate')(*temp_argv)
                else: # 一般の要素の場合
                    for elem in argument[1:]: # 2番目以降もマップ要素かどうか(例: Track.X.Interpolate(...) or Track.Position(...) )
                        if(elem.data == 'mapfunc'): # 関数なら探索終了
                            break
                        temp = getattr(temp, elem.children[0].lower()) # 対応するオブジェクトを取得
                    getattr(temp, argument[-1].children[0].lower())(*temp_argv) 
    def include_file(self, path): #外部ファイルインクルード
        input = loadheader.joinpath(self.environment.rootpath, path)
        interpreter = ParseMap(self.environment,self.parser)
        interpreter.load_files(input)
    def start(self, *argument):
        if(all(elem == None for elem in argument)):
            return self.environment
    def load_files(self, path, datastring = None, virtualroot = None, virtualfilename = None):
        if datastring is None:
            f_path, rootpath_tmp, f_encoding = loadheader.loadheader(path,'BveTs Map ',2)
            def readfile(filepath,fileencode):
                try:
                    f=open(filepath,'r',encoding=fileencode)
                    f.readline() #ヘッダー行空読み
                    linecount = 1

                    filebuffer = f.read()
                    f.close()
                except:
                    f.close()
                    raise
                return filebuffer
            if(self.isroot):
                self.environment.rootpath = rootpath_tmp #最上層のマップファイルの場合のみ、ルートパスを記録

            try: #ファイルオープン
                filebuffer = readfile(f_path,f_encoding)
            except UnicodeDecodeError as e: #ファイル指定のエンコードでオープンできない時
                if f_encoding.casefold() == 'utf-8':
                    encode_retry = 'CP932'
                else:
                    encode_retry = 'utf-8'
                print('Warning: '+str(f_path.name)+' cannot be decoded with '+f_encoding+'. Kobushi tries to decode with '+encode_retry+'.')
                filebuffer = readfile(f_path,encode_retry)
        else: # 実ファイルの代わりに文字列をパースする場合の処理
            filebuffer = datastring
            rootpath_tmp = virtualroot
            f_path = virtualfilename
            self.environment.rootpath = rootpath_tmp
            
        try: #構文解析
            tree = self.parser.parse(filebuffer)
        except Exception as e:
            raise RuntimeError('ParseError: in file '+str(f_path)+'\n'+str(e))

        #print(tree)
        #import pdb
        #pdb.set_trace()
        try: #ツリー処理
            self.transform(tree)
        except Exception as e:
            raise RuntimeError('IntepretationError: in file '+str(f_path)+', distance='+str(self.environment.variable['distance'])+'\n'+str(e))
            #print(self.environment.variable)
            
        
        if(self.isroot): # 最上層のマップファイルのロードが完了したら、データを距離でソート
            self.environment.controlpoints.relocate()
            self.environment.own_track.relocate()
            self.environment.othertrack.relocate()
        
        print(str(f_path.name)+' loaded.')
        return self.environment
