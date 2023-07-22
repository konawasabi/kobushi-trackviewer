'''
    Copyright 2021-2023 konawasabi

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
from . import loadheader
import re

class Environment():
    '''Mapの構成要素をまとめるクラス。
    self.rootpath:   Mapファイルの親ディレクトリへのパス
    self.variable:   変数を格納するdict
    self.own_track:  自軌道データを格納するオブジェクト
    self.station:    stationデータを格納するオブジェクト
    self.controlpoints: Map要素が指定されている距離程リスト
    '''
    def __init__(self):
        self.rootpath = ''
        self.predef_vars = {'distance':0.0}
        self.variable = {}
        self.own_track = Owntrack(self)
        self.station = Station(self)
        self.controlpoints = ControlPoints(self)
        self.othertrack = Othertrack(self)
class Owntrack():
    '''自軌道データクラス
    (1)パーサが読み取った自軌道マップ要素を変換するサブクラス
        curvefunc:      curve要素の操作
        legacyfunc:     legacy要素(turn, curve, pitch, fog)の操作
        gradientfunc:   gradient要素の操作
    (2)変数類
        self.data:          マップ要素リスト
        self.environment:   親クラス（Environment）への参照
        
    '''
    class curvefunc():
        def __init__(self,p):
            self.parent = p
        def setgauge(self, *a):
            self.parent.putdata('gauge',a[0])
        def gauge(self, *a):
            self.setgauge(*a)
        def setcenter(self, *a):
            self.parent.putdata('center',a[0])
        def setfunction(self, *a):
            self.parent.putdata('interpolate_func','sin' if a[0] == 0 else 'line')
        def begintransition(self, *a):
            self.parent.putdata('radius',None,'bt')
            self.parent.putdata('cant',None,'bt')
        def begincircular(self, *a):
            self.begin(*a)
        def begin(self, *a):
            if(len(a) == 2):
                self.parent.putdata('radius',a[0])
                self.parent.putdata('cant',a[1])
            elif(len(a) == 1):
                self.parent.putdata('radius',a[0])
                self.parent.putdata('cant',0)
        def end(self, *a):
            self.begin(0,0)
        def interpolate(self, *a):
            if(len(a) == 2):
                self.parent.putdata('radius',a[0],'i')
                self.parent.putdata('cant',a[1],'i')
            elif(len(a) == 1):
                self.parent.putdata('radius',a[0],'i')
                self.parent.putdata('cant',None,'i')
        def change(self, *a):
            self.begin(*a)
    class legacyfunc():
        def __init__(self,p):
            self.parent = p
        def turn(self, *a):
            self.parent.putdata('turn',a[0])
        def curve(self, *a):
            if(len(a) == 2):
                self.parent.putdata('radius',a[0])
                self.parent.putdata('cant',a[1])
            elif(len(a) == 1):
                self.parent.putdata('radius',a[0])
                self.parent.putdata('cant',0)
        def pitch(self, *a):
            self.parent.putdata('gradient',a[0])
        def fog(self, *a):
            return None
    class gradientfunc():
        def __init__(self,p):
            self.parent = p
        def begintransition(self, *a):
            self.parent.putdata('gradient',None,'bt')
        def begin(self, *a):
            self.parent.putdata('gradient',a[0])
        def beginconst(self, *a):
            self.begin(*a)
        def end(self, *a):
            self.begin(0)
        def interpolate(self, *a):
            self.parent.putdata('gradient',a[0],'i')
    
    def __init__(self, p):
        self.data = []
        
        self.x = []
        self.y = []
        
        self.position = []
        
        self.environment = p
        
        self.curve = self.curvefunc(self)
        self.legacy = self.legacyfunc(self)
        self.gradient = self.gradientfunc(self)
    
    def putdata(self,key,value,flag=''):
        '''dataリストへ要素をdictとして追加する。
        distance
            呼び出された時点でのdistance変数の値
        key
            マップ要素の種別
        value
            Noneの場合、'c':直前のコマンドで指定された値と同一を代入
        flag
            '':change, 'i':interpolate, 'bt':begintransition
        '''
        self.data.append({'distance':self.environment.predef_vars['distance'], 'value':'c' if value == None else value, 'key':key, 'flag':flag})
    def relocate(self):
        self.data = sorted(self.data, key=lambda x: x['distance'])
        
class Station():
    def load(self, *argvs):
        input = loadheader.joinpath(self.environment.rootpath, argvs[0]) #与えられたファイル名とrootpathから絶対パスを作成する。
        f_path, rootpath_tmp, f_encoding = loadheader.loadheader(input,'BveTs Station List ',0.04) #station listファイルかどうか判定する。
        
        def read_stationlist(path,file_encoding):
            result_stations = {}
            try:
                f=open(f_path,'r',encoding=file_encoding)
                f.readline() #ヘッダー行空読み
                while True:
                    buff = f.readline()
                    if(buff==''):# EOF?
                        break
                    buff = re.sub('#.*\n','\n',buff) #コメントを除去する
                    buff = re.sub('\t', '', buff) #tabを除去する
                    buff = re.sub(' ', '', buff) #スペースを除去する
                    if(buff=='\n' or buff.count(',')<1):#空白行（コメントのみの行など）、コンマ区切りが存在しない行なら次の行に進む。
                        continue
                    buff = buff.split(',')
                    result_stations[buff[0].lower()]=buff[1].replace('\"','')
                f.close()
            except:
                f.close()
                raise
            return result_stations
        try:
            self.stationkey = read_stationlist(f_path,f_encoding)
        except UnicodeDecodeError as e:
            if f_encoding.casefold() == 'utf-8':
                encode_retry = 'shift_jis'
            else:
                encode_retry = 'utf-8'
            try:
                self.stationkey = read_stationlist(f_path,encode_retry)
            except Exception as e:
                raise RuntimeError('File encoding error: '+str(f_path))
    def put(self, *argvs):
        #self.position.append({'distance':self.environment.variable['distance'], 'stationkey':argvs[0].lower()})
        self.position[self.environment.predef_vars['distance']]=argvs[0].lower()
    def __init__(self, parent):
        self.position = {}
        self.stationkey = {}
        self.environment = parent

class ControlPoints():
    '''マップ要素が存在する距離程のリストを作る
    '''
    def __init__(self, parent):
        self.list_cp = []
        self.environment = parent
    def add(self, value):
        self.list_cp.append(value)
    def relocate(self):
        '''self.list_cpについて、重複する要素を除去して距離順にソートする。
        '''
        self.list_cp = sorted(list(set(self.list_cp)))

class Othertrack():
    class setposition():
        def __init__(self, parent, dimension):
            self.parent = parent
            self.dimension = dimension
        def interpolate(self, *a):
            if(len(a)==1):
                self.parent.putdata(a[0],self.dimension+'.position',None)
                self.parent.putdata(a[0],self.dimension+'.radius',None)
            elif(len(a)==2):
                self.parent.putdata(a[0],self.dimension+'.position',a[1])
                self.parent.putdata(a[0],self.dimension+'.radius',None)
            elif(len(a)>=3):
                self.parent.putdata(a[0],self.dimension+'.position',a[1])
                self.parent.putdata(a[0],self.dimension+'.radius',a[2])
    class cantfunc():
        def __init__(self, parent):
            self.parent = parent
        def setgauge(self, *a):
            self.parent.putdata(a[0],'gauge',a[1])
        def setcenter(self, *a):
            self.parent.putdata(a[0],'center',a[1])
        def setfunction(self, *a):
            self.parent.putdata(a[0],'interpolate_func','sin' if a[1] == 0 else 'line')
        def begintransition(self, *a):
            self.parent.putdata(a[0],'cant',None,'bt')
        def begin(self, *a):
            self.parent.putdata(a[0],'cant',a[1],'i')
        def end(self, *a):
            self.parent.putdata(a[0],'cant',0,'i')
        def interpolate(self, *a):
            if len(a) == 1:
                self.parent.putdata(a[0],'cant',None,'i')
            else:
                self.parent.putdata(a[0],'cant',a[1],'i')
    def __init__(self,p):
        self.data = {}
        self.environment = p
        self.x = self.setposition(self, 'x')
        self.y = self.setposition(self, 'y')
        self.cant = self.cantfunc(self)
    
    def position(self, *a):
        if(len(a)==3):
            self.x.interpolate(a[0],a[1] if a[1] != None else 0,0)
            self.y.interpolate(a[0],a[2] if a[2] != None else 0,0)
        elif(len(a)==4):
            self.x.interpolate(a[0],a[1] if a[1] != None else 0,a[3] if a[3] != None else 0)
            self.y.interpolate(a[0],a[2] if a[2] != None else 0,0)
        elif(len(a)>=5):
            self.x.interpolate(a[0],a[1] if a[1] != None else 0,a[3] if a[3] != None else 0)
            self.y.interpolate(a[0],a[2] if a[2] != None else 0,a[4] if a[4] != None else 0)
    def gauge(self, *a):
        '''Cant.SetGaugeの旧表記
        '''
        self.cant.setgauge(*a)
    def putdata(self,trackkey,elementkey,value,flag=''):
        '''dataリストへ要素をdictとして追加する。
        trackkey
            他軌道キー
        elementkey
            マップ要素の種別
                'x.position' : x方向座標
                'x.radius'   : x方向相対半径
                'y.position' : y方向座標
                'y.radius'   : y方向相対半径
        value
            Noneの場合、'c':直前のコマンドで指定された値と同一を代入
        flag
            '':change, 'i':interpolate, 'bt':begintransition
        '''
        if type(trackkey) == float:
            trackkey_lc = str(int(trackkey)).lower()
        else:
            trackkey_lc = str(trackkey).lower()
        if trackkey_lc not in self.data.keys():
            self.data[trackkey_lc] = []
        self.data[trackkey_lc].append({'distance':self.environment.predef_vars['distance'], 'value':'c' if value == None else value, 'key':elementkey, 'flag':flag})
    def relocate(self):
        self.cp_range = {}
        for trackkey in self.data.keys():
            self.data[trackkey]     = sorted(self.data[trackkey], key=lambda x: x['distance'])
            self.cp_range[trackkey] = {'min':min(self.data[trackkey], key=lambda x: x['distance'])['distance'],'max':max(self.data[trackkey], key=lambda x: x['distance'])['distance']}
