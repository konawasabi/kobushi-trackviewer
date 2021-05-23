class Environment():
    def __init__(self):
        self.variable = {'distance':0.0}
        self.own_track = Owntrack(self)
        self.station = Station(self)

class Owntrack():
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
        """
        valueについて、'c':直前のコマンドで指定された値と同一
        typeについて、'':change, 'i':interpolate, 'bt':begintransition
        """
        self.data.append({'distance':self.environment.variable['distance'], 'value':'c' if value == None else value, 'key':key, 'flag':flag})
        
class Station():
    def load(self, *argvs):
        pass
    def put(self, *argvs):
        self.position.append({'distance':self.environment.variable['distance'], 'stationkey':argvs[0]})
    def __init__(self, parent):
        self.position = []
        self.stationkey = {}
        self.environment = parent
