import numpy as np
import trackcoordinate as tc

class TrackGenerator():
    def __init__(self,environment,x0=None,y0=None,z0=None,theta0=None,r0=None,gr0=None,dist0=None):
        self.env = environment
        self.data_ownt = self.env.own_track.data
        self.list_cp = self.env.controlpoints.list_cp
        
        # マップ要素が存在する距離程の最小, 最大値
        self.cp_min = min(self.list_cp)
        self.cp_max = max(self.list_cp)
        
        # 等間隔で距離程を追加する
        equaldist_unit = 25
        if(len(self.env.station.position) > 0): # 駅が設定されている区間or距離程が存在する区間の前後500mに追加
            self.stationdist_min = round(min(self.env.station.position.keys()),-1) - 500
            self.stationdist_max = round(max(self.env.station.position.keys()),-1) + 500
            cp_equaldist = np.arange(self.stationdist_min,self.stationdist_max,equaldist_unit)
            self.list_cp.extend(cp_equaldist)
            self.list_cp = sorted(list(set(self.list_cp)))
        else:
            cp_equaldist = np.arange(round(self.cp_min,-1) - 500,round(self.cp_max,-1) + 500,equaldist_unit)
            self.list_cp.extend(cp_equaldist)
            self.list_cp = sorted(list(set(self.list_cp)))
        
        # 前回処理した地点の情報
        self.last_pos = {}
        self.last_pos['x']        = x0     if x0     != None else 0
        self.last_pos['y']        = y0     if y0     != None else 0
        self.last_pos['z']        = z0     if z0     != None else 0
        self.last_pos['theta']    = theta0 if theta0 != None else 0
        self.last_pos['radius']   = r0     if r0     != None else 0
        self.last_pos['gradient'] = gr0    if gr0    != None else 0
        self.last_pos['distance'] = dist0  if dist0  != None else min(self.list_cp)
        
        #座標情報を格納するリスト
        self.result = [[self.last_pos['distance'],self.last_pos['x'],self.last_pos['y'],self.last_pos['z'],self.last_pos['theta'],self.last_pos['radius'],self.last_pos['gradient']]]
    def generate_owntrack(self):
        '''マップ要素が存在する全ての距離程(self.list_cp)に対して自軌道の座標データを生成する。
        self.env: マップ要素が格納されたEnvironmentオブジェクト。
        結果はself.result に[[distance,xpos,ypos,zpos,theta,radius,gradient],[d.,x.,y.,...],[...],...]として格納する。
        '''
        radius_p   = TrackPointer(self.env,'radius')
        gradient_p = TrackPointer(self.env,'gradient')
        turn_p     = TrackPointer(self.env,'turn')
        
        grad_gen = tc.gradient_intermediate()
        curve_gen = tc.curve_intermediate()
        
        if not __debug__: # -O オプションが指定されている時のみ、デバッグ情報を処理
            # numpy RuntimeWarning発生時に当該点の距離程を印字
            def print_warning_position(err,flag):
                print('Numpy warning: '+str(err)+', '+str(flag)+' at '+str(dist))
                raise
            np.seterr(all='call')
            np.seterrcall(print_warning_position)
            ''' デバッガ関係は__main__部で取り扱う
            # エラーが発生した場合、デバッガを起動 https://gist.github.com/podhmo/5964702e7471ccaba969105468291efa
            def info(type, value, tb):
                if hasattr(sys, "ps1") or not sys.stderr.isatty():
                    # You are in interactive mode or don't have a tty-like
                    # device, so call the default hook
                    sys.__excepthook__(type, value, tb)
                else:
                    import traceback, pdb

                    # You are NOT in interactive mode; print the exception...
                    traceback.print_exception(type, value, tb)
                    # ...then start the debugger in post-mortem mode
                    pdb.pm()
            import sys
            sys.excepthook = info
            '''
        for dist in self.list_cp:
            # radiusに対する処理
            while (radius_p.overNextpoint(dist)): #注目している要素区間の終端を超えたか？
                if(radius_p.seekoriginofcontinuous(radius_p.pointer['next']) != None):
                    self.last_pos['radius'] = self.data_ownt[radius_p.seekoriginofcontinuous(radius_p.pointer['next'])]['value']
                radius_p.seeknext()
            if(radius_p.pointer['last'] == None): # 最初のcurve要素に到達していない場合
                if(self.last_pos['radius'] == 0):
                    [x, y] =curve_gen.straight(self.data_ownt[radius_p.pointer['next']]['distance'] - self.cp_min, self.last_pos['theta'], dist - self.last_pos['distance'])
                    tau = 0
                    radius = self.last_pos['radius']
                else:
                    [x, y], tau =curve_gen.circular_curve(self.data_ownt[radius_p.pointer['next']]['distance'] - self.cp_min, self.last_pos['theta'], dist - self.last_pos['distance'])
                    radius = self.last_pos['radius']
            elif(radius_p.pointer['next'] == None): # curve要素リスト終端に到達
                if(self.last_pos['radius'] == 0): # 曲線半径が0 (直線)の場合
                    [x, y] = curve_gen.straight(self.cp_max - self.last_pos['distance'],\
                                              self.last_pos['theta'],\
                                              dist - self.last_pos['distance'])
                    tau = 0
                else: # 一定半径の曲線の場合
                    [x, y], tau = curve_gen.circular_curve(self.cp_max - self.last_pos['distance'],\
                                                         self.last_pos['radius'],\
                                                         self.last_pos['theta'],\
                                                         dist - self.last_pos['distance'])
                radius = self.last_pos['radius']
            else: # 一般の場合の処理
                if(self.data_ownt[radius_p.pointer['next']]['value'] == 'c'): # 曲線半径が変化しない区間かどうか
                    if(self.last_pos['radius'] == 0): # 曲線半径が0 (直線)の場合
                        [x, y] = curve_gen.straight(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                  self.last_pos['theta'],\
                                                  dist - self.last_pos['distance'])
                        tau = 0
                    else: # 一定半径の曲線の場合
                        [x, y], tau = curve_gen.circular_curve(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                             self.last_pos['radius'],\
                                                             self.last_pos['theta'],\
                                                             dist - self.last_pos['distance'])
                    radius = self.last_pos['radius']
                else: # 曲線半径が変化する場合
                    if(self.data_ownt[radius_p.pointer['next']]['flag'] == 'i' or self.data_ownt[radius_p.pointer['last']]['flag'] == 'bt'): # interpolateフラグがある
                        if(self.last_pos['radius'] != self.data_ownt[radius_p.pointer['next']]['value']): # 注目区間前後で異なる曲線半径を取るなら緩和曲線を出力
                            [x, y], tau, radius = curve_gen.transition_curve(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                                       self.last_pos['radius'],\
                                                                       self.data_ownt[radius_p.pointer['next']]['value'],\
                                                                       self.last_pos['theta'],\
                                                                       'line',\
                                                                       dist - self.last_pos['distance'])
                        elif(self.data_ownt[radius_p.pointer['next']]['value'] != 0): # 曲線半径が変化せず、!=0の場合は円軌道を出力
                            [x, y], tau = curve_gen.circular_curve(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                            self.last_pos['radius'],\
                            self.last_pos['theta'],\
                            dist - self.last_pos['distance'])
                            radius = self.last_pos['radius']
                        else: # 直線軌道を出力
                            [x, y] = curve_gen.straight(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                      self.last_pos['theta'],\
                                                      dist - self.last_pos['distance'])
                            tau = 0
                            radius = self.last_pos['radius']
                    else: # interpolateでない
                        if(self.last_pos['radius'] == 0): # 曲線半径が0 (直線)の場合
                            [x, y] = curve_gen.straight(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                      self.last_pos['theta'],\
                                                      dist - self.last_pos['distance'])
                            tau = 0
                        else: # 一定半径の曲線の場合
                            [x, y], tau = curve_gen.circular_curve(self.data_ownt[radius_p.pointer['next']]['distance'] - self.last_pos['distance'],\
                                                                 self.last_pos['radius'],\
                                                                 self.last_pos['theta'],\
                                                                 dist - self.last_pos['distance'])
                        radius = self.last_pos['radius']
            # turnに対する処理
            
            # gradientに対する処理
            while(gradient_p.overNextpoint(dist)): #注目している要素区間の終端を超えたか？
                if(gradient_p.seekoriginofcontinuous(gradient_p.pointer['next']) != None):
                    self.last_pos['gradient'] = self.data_ownt[gradient_p.seekoriginofcontinuous(gradient_p.pointer['next'])]['value']
                gradient_p.seeknext()
            if(gradient_p.pointer['last'] == None): #最初の勾配要素に到達していない
                if(gradient_p.pointer['next'] == None): # 勾配が存在しないmapの場合の処理
                    z = grad_gen.straight(self.cp_max - self.cp_min, self.last_pos['gradient'], dist - self.last_pos['distance'])
                else:
                    z = grad_gen.straight(self.data_ownt[gradient_p.pointer['next']]['distance'] - self.cp_min, self.last_pos['gradient'], dist - self.last_pos['distance'])
                gradient = self.last_pos['gradient']
            elif(gradient_p.pointer['next'] == None): #最後の勾配要素を通過した
                z = grad_gen.straight(self.cp_max - self.last_pos['distance'], self.last_pos['gradient'], dist - self.last_pos['distance'])
                gradient = self.last_pos['gradient']
            else: # 一般の場合の処理
                if(self.data_ownt[gradient_p.pointer['next']]['value'] == 'c'): # 注目区間の前後で勾配が変化しない場合
                    z = grad_gen.straight(self.data_ownt[gradient_p.pointer['next']]['distance'] - self.last_pos['distance'], self.last_pos['gradient'], dist - self.last_pos['distance'])
                    gradient = self.last_pos['gradient']
                else:
                    if(self.data_ownt[gradient_p.pointer['next']]['flag'] == 'i' or self.data_ownt[gradient_p.pointer['last']]['flag'] == 'bt'): # interpolateフラグがある場合
                        if(self.last_pos['gradient'] != self.data_ownt[gradient_p.pointer['next']]['value']): # 注目区間の前後で勾配が変化するなら縦曲線を出力
                            [tmp_d, z], gradient = grad_gen.transition(self.data_ownt[gradient_p.pointer['next']]['distance'] - self.last_pos['distance'],self.last_pos['gradient'],self.data_ownt[gradient_p.pointer['next']]['value'],dist - self.last_pos['distance'])
                        else: # 一定勾配を出力
                            z = grad_gen.straight(self.data_ownt[gradient_p.pointer['next']]['distance'] - self.last_pos['distance'], self.last_pos['gradient'], dist - self.last_pos['distance'])
                            gradient = self.last_pos['gradient']
                    else: # interpolateでない場合、一定勾配を出力
                        z = grad_gen.straight(self.data_ownt[gradient_p.pointer['next']]['distance'] - self.last_pos['distance'], self.last_pos['gradient'], dist - self.last_pos['distance'])
                        gradient = self.last_pos['gradient']
            
            # 地点情報を更新
            self.last_pos['x']       += x
            self.last_pos['y']       += y
            self.last_pos['z']       += z
            self.last_pos['theta']   += tau
            self.last_pos['radius']   = radius
            self.last_pos['gradient'] = gradient
            self.last_pos['distance'] = dist
            # 座標リストに追加
            self.result.append([self.last_pos['distance'],self.last_pos['x'],self.last_pos['y'],self.last_pos['z'],self.last_pos['theta'],self.last_pos['radius'],self.last_pos['gradient']])
            
        return np.array(self.result)
class TrackPointer():
    def __init__(self,environment,target):
        self.pointer = {'last':None, 'next':0}
        self.env = environment
        self.target = target
        self.data = self.env.own_track.data
        self.ix_max = len(self.data) - 1
        
        self.seekfirst()
    def seek(self, ix0):
        '''ix0以降で注目する要素が現れるインデックスを探索。データ終端まで到達した場合はNoneを返す。
        '''
        ix = ix0
        while True:
            if (ix > self.ix_max):
                ix = None
                break
            if(self.data[ix]['key'] != self.target):
                ix+=1
            else:
                break
        return ix
    def seekfirst(self):
        '''注目する要素が初めて現れるインデックスを探索して、pointer['next']にセットする。
        '''
        self.pointer['next'] = self.seek(0)
    def seeknext(self):
        '''次の要素が存在するインデックスを探し、self.pointer['last', 'next']を書き換える。
        self.pointer['next'] == None の場合は何もしない。
        '''
        if(self.pointer['next'] != None):
            self.pointer['last'] = self.pointer['next']
            self.pointer['next'] = self.seek(self.pointer['next']+1)
    def insection(self,distance):
        '''注目している要素の区間内かどうか調べる。
        self.pointer['last'] < 与えられたdistance <= self.pointer['next'] ならTrue
        '''
        return (self.data[self.pointer['prev']]['distance'] > distance and self.data[self.pointer['next']]['distance'] <= distance)
    def onNextpoint(self,distance):
        '''注目している要素区間の終端にいるか調べる。
        与えられたdistance == 注目しているpointer['next'] ならTrue。
        pointer['next'] == None (要素リスト終端に到達した) なら必ずFalse。
        '''
        return (self.data[self.pointer['next']]['distance'] == distance) if self.pointer['next'] != None else False
    def overNextpoint(self,distance):
        '''注目している要素区間を超えたか調べる。
        与えられたdistance > 注目しているpointer['next'] ならTrue。
        pointer['next'] == None (要素リスト終端に到達した) なら必ずFalse。
        '''
        return (self.data[self.pointer['next']]['distance'] < distance) if self.pointer['next'] != None else False
    def beforeLastpoint(self,distance):
        '''注目している要素区間にまだ到達していないか調べる。
        与えられたdistance <= 注目しているpointer['last'] ならTrue。
        pointer['last'] == None (リスト始端の要素地点に到達していない) なら必ずTrue。
        '''
        return (self.data[self.pointer['last']]['distance'] >= distance) if self.pointer['last'] != None else True
    def seekoriginofcontinuous(self,index):
        '''注目している要素のvalue=c (直前に指定した値と同一)であった場合、その起源となる要素(value != c)を示すインデックスを返す。
        リストの先頭まで探索しても見つからなかった場合はNoneを返す。
        '''
        if(index != None):
            while True:
                if(self.data[index]['key'] == self.target and self.data[index]['value'] != 'c'):
                    break
                else:
                    index -= 1
                    if(index < 0):
                        index = None
                        break
        return index
            
class OtherTrackGenerator():
    class OtherTrackPointer(TrackPointer):
        def __init__(self,environment,target,trackkey):
            super().__init__(environment,target)
            self.data = environment.othertrack.data[trackkey]
            self.ix_max = len(self.data) - 1
            self.seekfirst()
        
    def __init__(self,environment,trackkey):
        self.env = environment
        self.trackkey = trackkey
        self.data = self.env.othertrack.data[trackkey]
        self.owntrack_position = self.env.owntrack_pos
        self.result = []
        self.distrange={'min':min(self.data, key=lambda x: x['distance'])['distance'], 'max':max(self.data, key=lambda x: x['distance'])['distance']}
        # 前回処理した地点の情報
        self.pos = {'last':{}, 'next':{}}
        for key in ['x.position','x.radius','x.distance','y.position','y.radius','y.distance']:
            self.pos['last'][key] = 0
            self.pos['next'][key] = 0
    
    def generate(self):
        '''他軌道座標を計算する。
        対象はインスタンス作成時に指定したkeyの軌道。
        '''
        track_gen = tc.OtherTrack() # 座標計算オブジェクト
        # 軌道要素ポインタの作成
        trackptr = {}
        trackptr['x.position'] = self.OtherTrackPointer(self.env,'x.position',self.trackkey)
        trackptr['x.radius']   = self.OtherTrackPointer(self.env,'x.radius',self.trackkey)
        trackptr['y.position'] = self.OtherTrackPointer(self.env,'y.position',self.trackkey)
        trackptr['y.radius']   = self.OtherTrackPointer(self.env,'y.radius',self.trackkey)
        #tp_keys = ['x.position','x.radius','y.position','y.radius']
        #skip_dimension = {'x.position':False, 'x.radius':False, 'y.position':False, 'y.radius':False}
        for element in self.owntrack_position: # 自軌道が指定されている全ての距離程について計算する
            if self.distrange['min'] > element[0]: # 対象となる軌道が最初に現れる距離程にまだ達していないか？
                continue
            for tpkey in trackptr.keys(): # ポインタを進める
                while trackptr[tpkey].overNextpoint(element[0]):
                    trackptr[tpkey].seeknext()
                    if trackptr[tpkey].pointer['next'] != None:
                        self.pos['last'][tpkey] = self.pos['next'][tpkey]
                        k = 'next'
                        newval = self.data[trackptr[tpkey].pointer[k]]['value']
                        self.pos[k][tpkey] = newval if newval != 'c' else self.pos['last'][tpkey]
            if trackptr['x.position'].pointer['last'] != None and trackptr['x.position'].pointer['next'] != None: # skip_dimension に従って計算するかどうか判断する
                for k in ['last','next']:
                    self.pos[k]['x.distance'] = self.data[trackptr['x.position'].pointer[k]]['distance']
                
                temp_result_X = track_gen.absolute_position_X(self.pos['next']['x.distance'] - self.pos['last']['x.distance'],\
                 self.pos['next']['x.radius'],\
                 self.pos['last']['x.position'],\
                 self.pos['next']['x.position'],\
                 element[0] - self.pos['last']['x.distance'],\
                 element)
            else:
                temp_result_X = np.dot(track_gen.rotate(element[4]), np.array([0,self.pos['last']['x.position']])) + np.array([element[1],element[2]])
            if trackptr['y.position'].pointer['last'] != None and trackptr['y.position'].pointer['next'] != None:
                for k in ['last','next']:
                    self.pos[k]['y.distance'] = self.data[trackptr['y.position'].pointer[k]]['distance']
                temp_result_Y = track_gen.absolute_position_Y(self.pos['next']['y.distance'] - self.pos['last']['y.distance'],\
                 self.pos['next']['y.radius'],\
                 self.pos['last']['y.position'],\
                 self.pos['next']['y.position'],\
                 element[0] - self.pos['last']['y.distance'],\
                 element)
            else:
                temp_result_Y = [0,self.pos['last']['y.position']]+ np.array([element[1],element[3]])
            self.result.append([element[0],temp_result_X[0],temp_result_X[1],temp_result_Y[1]])
        return np.array(self.result)
