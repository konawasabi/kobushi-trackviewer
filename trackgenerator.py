import numpy as np
import trackcoordinate as tc

class TrackGenerator():
    def __init__(self,environment,x0=None,y0=None,theta0=None,r0=None,gr0=None,dist0=None):
        self.env = environment
        self.data_ownt = self.env.own_track.data
        self.list_cp = self.env.controlpoints.list_cp
        
        self.cp_min = min(self.list_cp)
        self.cp_max = max(self.list_cp)
        
        self.current_pos = {}
        self.current_pos['x']        = x0     if x0     != None else 0
        self.current_pos['y']        = y0     if y0     != None else 0
        self.current_pos['theta']    = theta0 if theta0 != None else 0
        self.current_pos['radius']   = r0     if r0     != None else 0
        self.current_pos['gradient'] = gr0    if gr0    != None else 0
        self.current_pos['distance'] = dist0  if dist0  != None else self.cp_min
        
        self.result = None
    def generate_owntrack(self):
        '''マップ要素が存在する全ての距離程(self.list_cp)に対して自軌道の座標データを生成する。
        self.env: マップ要素が格納されたEnvironmentオブジェクト。
        結果はself.data_ownt.position にnp.array([distance,xpos,ypos],[d.,x.,y.],[...],...)として格納する。
        '''
        radius_p   = self.TrackPaser(self.env,'radius')
        gradient_p = self.TrackParser(self.env,'gradient')
        
    class TrackPaser():
        def __init__(self,environment,target):
            self.pointer = {'last':0, 'next':0}
            self.env = environment
            self.target = target
            self.data = self.env.own_track.data
            self.ix_max = len(self.data) - 1
            self.seeknext()
        def seeknext(self):
            ix = self.pointer['next']
            while True:
                ix +=1
                if(ix == self.ix_max):
                    break
                if(self.data[ix]['key'] == self.target):
                    self.pointer['last'] = self.pointer['next']
                    self.pointer['next'] = ix
                    break
        def isinsection(self,distance):
            '''距離程distanceがself.pointer['last'] ~ self.pointer['next']の要素が示す区間内に含まれているか判定。
            含まれていればTrueを返す。
            '''
            if(self.data[self.pointer['next']]['distance'] < distance):
                return True
            else:
                return False
