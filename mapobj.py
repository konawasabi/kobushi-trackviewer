import loadheader
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
        self.variable = {'distance':0.0}
        self.own_track = Owntrack(self)
        self.station = Station(self)
        self.controlpoints = ControlPoints(self)

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
        self.data.append({'distance':self.environment.variable['distance'], 'value':'c' if value == None else value, 'key':key, 'flag':flag})
    def relocate(self):
        self.data = sorted(self.data, key=lambda x: x['distance'])
        
class Station():
    def load(self, *argvs):
        input = loadheader.joinpath(self.environment.rootpath, argvs[0]) #与えられたファイル名とrootpathから絶対パスを作成する。
        f, filename, rootpath_tmp = loadheader.loadheader(input,'BveTs Station List ',2) #station listファイルかどうか判定する。okならファイルポインタが帰ってくる。
        f.readline() #ヘッダー行空読み
        while True:
            buff = f.readline()
            if(buff==''):# EOF?
                break
            buff = re.sub('#.*\n','\n',buff) #コメントを除去する
            if(buff=='\n'):#空白行（コメントのみの行だったもの）なら次の行に進む。
                continue
            buff = buff.split(',')
            self.stationkey[buff[0].lower()]=buff[1]
        f.close()
    def put(self, *argvs):
        self.position.append({'distance':self.environment.variable['distance'], 'stationkey':argvs[0].lower()})
    def __init__(self, parent):
        self.position = []
        self.stationkey = {}
        self.environment = parent

class ControlPoints():
    def __init__(self, parent):
        self.list_cp = []
        self.environment = parent
    def add(self, value):
        self.list_cp.append(value)
    def relocate(self):
        self.list_cp = sorted(list(set(self.list_cp)))
