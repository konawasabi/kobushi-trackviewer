class Environment():
    def __init(self):
        self.variable = {'distance':0.0}

class Owntrack():
    class curvefunc():
        def __init__(self,p):
            self.parent = p
        def setgauge(self):
            pass
        def gauge(self):
            self.setgauge()
        def setcenter(self):
            pass
        def setfunction(self):
            pass
        def begintransition(self):
            pass
        def begincircular(self):
            self.begin()
        def begin(self):
            pass
        def end(self):
            pass
        def interpolate(self):
            pass
        def change(self):
            pass
    class legacyfunc():
        def __init__(self,p):
            self.parent = p
        def turn(self):
            pass
        def curve(self):
            pass
        def pitch(self):
            pass
    class gradientfunc():
        def __init__(self,p):
            self.parent = p
        def begintransition(self):
            pass
        def begin(self):
            self.begintransition()
        def beginconst(self):
            pass
        def end(self):
            pass
        def interpolate(self):
            pass
    
    def __init__(self, p):
        self.gradient = []
        self.radius = []
        self.cant = []
        self.gauge = []
        self.center = []
        self.interpolate_func = []
        
        self.x = []
        self.y = []
        
        self.environment = p
        
        self.curve = self.curvefunc(self)
        self.legacy = self.legacyfunc(self)
        self.gradient = self.gradientfunc(self)
    
    
