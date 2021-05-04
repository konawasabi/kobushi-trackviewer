class Environment():
    def __init__(self):
        self.variable = {'distance':0.0}
        self.own_track = Owntrack(self)

class Owntrack():
    class curvefunc():
        def __init__(self,p):
            self.parent = p
        def setgauge(self, *a):
            self.parent.data['gauge'].append([self.parent.environment.variable['distance'], a[0]])
        def gauge(self, *a):
            self.setgauge(*a)
        def setcenter(self, *a):
            self.parent.data['center'].append([self.parent.environment.variable['distance'], a[0]])
        def setfunction(self, *a):
            self.parent.data['interpolate_func'].append([self.parent.environment.variable['distance'], 'sin' if a[0] == 0 else 'line'])
        def begintransition(self, *a):
            self.interpolate(None)
        def begincircular(self, *a):
            self.begin(*a)
        def begin(self, *a):
            self.interpolate(*a)
        def end(self, *a):
            self.interpolate(0,0)
        def interpolate(self, *a):
            if(len(a) == 2):
                self.parent.data['radius'].append([self.parent.environment.variable['distance'], 'i' if a[0] == None else a[0]])
                self.parent.data['cant'].append([self.parent.environment.variable['distance'],   'i' if a[1] == None else a[1]])
            elif(len(a) == 1):
                self.parent.data['radius'].append([self.parent.environment.variable['distance'], 'i' if a[0] == None else a[0]])
                self.parent.data['cant'].append([self.parent.environment.variable['distance'],   'i'])
        def change(self, *a):
            self.begin(*a)
    class legacyfunc():
        def __init__(self,p):
            self.parent = p
        def turn(self, *a):
            self.parent.data['turn'].append([self.parent.environment.variable['distance'], a[0]])
        def curve(self, *a):
            if(len(a) == 2):
                self.parent.data['radius'].append([self.parent.environment.variable['distance'], a[0]])
                self.parent.data['cant'].append([self.parent.environment.variable['distance'],   0 if a[1] == None else a[1]])
            elif(len(a) == 1):
                self.parent.data['radius'].append([self.parent.environment.variable['distance'], a[0]])
                self.parent.data['cant'].append([self.parent.environment.variable['distance'],   0])
        def pitch(self, *a):
            self.parent.data['gradient'].append([self.parent.environment.variable['distance'], a[0]])
    class gradientfunc():
        def __init__(self,p):
            self.parent = p
        def begintransition(self, *a):
            self.interpolate(None)
        def begin(self, *a):
            self.interpolate(*a)
        def beginconst(self, *a):
            self.begin(*a)
        def end(self, *a):
            self.interpolate(0)
        def interpolate(self, *a):
            self.parent.data['gradient'].append([self.parent.environment.variable['distance'], 'i' if a[0] == None else a[0]])
    
    def __init__(self, p):
        self.data = {}
        self.data['gradient'] = []
        self.data['radius'] = []
        self.data['cant'] = []
        self.data['gauge'] = []
        self.data['center'] = []
        self.data['interpolate_func'] = []
        self.data['turn'] = []
        
        self.x = []
        self.y = []
        
        self.environment = p
        
        self.curve = self.curvefunc(self)
        self.legacy = self.legacyfunc(self)
        self.gradient = self.gradientfunc(self)
    
    
