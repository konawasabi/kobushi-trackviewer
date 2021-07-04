import numpy as np
import trackcoordinate as tc
import trackgenerator as tgen

def plot_vetical_profile(environment, ax_g, ax_r):
    '''線路縦断面図を作成する。
    environment: Environmentオブジェクト
    ax_g: 勾配図を格納するaxes
    ax_r: 曲線図を格納するaxes
    '''
    input_d = environment.own_track.data
    previous_pos_gradient = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'gradient':0}
    previous_pos_radius   = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'radius':0}
    ix = 0
    
    gradient_gen = tc.gradient()
    curve_gen = tc.curve()
    
    output_gradient = np.array([0,0])
    output_radius = np.array([0,0])
    while (ix < len(input_d)):
        #from IPython.core.debugger import Pdb; Pdb().set_trace()
        if(input_d[ix]['key'] == 'gradient'):
            if(input_d[ix]['distance'] != previous_pos_gradient['distance']):
                if (input_d[ix]['value']=='c'): # 現在点の勾配 = 直前点の勾配なら、直線スロープを出力
                    res = gradient_gen.straight(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'])
                    gradient = previous_pos_gradient['gradient']
                else:
                    if(previous_pos_gradient['is_bt']): # 直前点がbegin_transitionなら、縦曲線を出力
                        res = gradient_gen.transition(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'],input_d[ix]['value'])
                    else:
                        if(input_d[ix]['flag'] == 'i'): # 現在点はinterpolateか？　Falseなら直前点の勾配の直線スロープを出力
                            if(input_d[ix]['value'] != previous_pos_gradient['gradient']): # 現在点がinterpolateで、直前点と異なる勾配なら、縦曲線を出力
                                res = gradient_gen.transition(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'],input_d[ix]['value'])
                            else:
                                res = gradient_gen.straight(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'])
                        else:
                            res = gradient_gen.straight(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'])
                    gradient = input_d[ix]['value']
                    
                output_gradient = np.vstack((output_gradient,res+output_gradient[-1]))
            previous_pos_gradient['distance'] = input_d[ix]['distance']
            previous_pos_gradient['y']        = output_gradient[-1][1]
            previous_pos_gradient['is_bt']    = True if input_d[ix]['flag']=='bt' else False
            previous_pos_gradient['gradient'] = gradient
        elif(input_d[ix]['key'] == 'radius'):
            if (input_d[ix]['value']=='c'):
                new_radius = previous_pos_radius['radius']
                result = np.array([input_d[ix]['distance'],new_radius])
            else:
                new_radius = np.sign(input_d[ix]['value']) # 曲線半径の符号を取り出す
                if(previous_pos_radius['is_bt']): # 直前点がbegin_transitionなら、緩和曲線を出力
                    result = np.array([input_d[ix]['distance'],new_radius])
                else:
                    if(input_d[ix]['flag'] == 'i'): # 現在点がinterpolateなら、緩和曲線を出力
                        result = np.array([input_d[ix]['distance'],new_radius])
                    else: # 現在点で階段状に変化する半径を出力
                        result = np.vstack((np.array([input_d[ix]['distance'],previous_pos_radius['radius']]),np.array([input_d[ix]['distance'],new_radius])))
            
            output_radius = np.vstack((output_radius,result))
            
            previous_pos_radius['distance'] = input_d[ix]['distance']
            previous_pos_radius['y']        = output_radius[-1][1]
            previous_pos_radius['is_bt']    = True if input_d[ix]['flag']=='bt' else False
            previous_pos_radius['radius']   = new_radius
        ix+=1
    
    ax_g.plot(output_gradient[:,0],output_gradient[:,1]) #勾配が存在しないmapだとoutput_gradientが空->エラーになる
    ax_r.plot(output_radius[:,0],output_radius[:,1])
    
    #ax_r.set_xlim([0,5000])
    #ax_g.set_xlim([0,5000])
    #ax.scatter(output[:,0],output[:,1],marker='+')


def plot_planer_map(environment, ax):
    '''線路平面図を作成する。
    environment: Environmentオブジェクト
    ax: 描画結果を格納するaxesオブジェクト
    '''
    input_d = environment.own_track.data
    previous_pos = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'radius':0}
    ix = 0
    
    gradient_gen = tc.gradient()
    curve_gen = tc.curve()
    
    output = np.array([[0,0]])
    #track_coarse = np.array([[0,0,0]])
    
    if not __debug__: # -O オプションが指定されている時のみ、デバッグ情報を処理
        # numpy RuntimeWarning発生時に当該点の距離程を印字
        def print_warning_position(err,flag):
            print('Numpy warning: '+str(err)+', '+str(flag)+' at '+str(input_d[ix]['distance']))
        np.seterr(all='call')
        np.seterrcall(print_warning_position)
        
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
    
    while (ix < len(input_d)):
        if(input_d[ix]['key'] == 'radius'): # 現在点がradiusかどうか
            if(input_d[ix]['distance'] != previous_pos['distance']):
                if (input_d[ix]['value']=='c'): # 現在点の半径 = 直前点の半径かどうか
                    if(previous_pos['radius']==0): # 直前点の半径 = 0 なら直線軌道を出力
                        res = curve_gen.straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                        theta = previous_pos['theta']
                    else: # 円軌道を出力
                        res, theta = curve_gen.circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                        theta += previous_pos['theta']
                    radius = previous_pos['radius']
                else:
                    if(previous_pos['is_bt'] or input_d[ix]['flag'] == 'i'): # 直前点がbegin_transition or 現在点がinterpolateなら、緩和曲線を出力
                        if(previous_pos['radius'] != input_d[ix]['value']):
                            res, theta = curve_gen.transition_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],input_d[ix]['value'],previous_pos['theta'], 'line')
                            theta += previous_pos['theta']
                        elif(input_d[ix]['value'] != 0): #曲線半径が変化しないTransition（カントのみ変化するような場合）では、円軌道(value!=0)or直線軌道(value==0)を出力
                            res, theta = curve_gen.circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                            theta += previous_pos['theta']
                        else:
                            res = curve_gen.straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                            theta = previous_pos['theta']
                    else: # interpolateしない場合
                        if(previous_pos['radius']==0): # 直前点の半径が0の場合、現在点までの直線軌道を出力
                            res = curve_gen.straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                            theta = previous_pos['theta']
                        else: # 現在点までの円軌道を出力
                            res, theta = curve_gen.circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                            theta += previous_pos['theta']
                    radius = input_d[ix]['value']
                output = np.vstack((output,res+output[-1]))
            else: # 現在点が直前点と同じ距離程の場合、軌道座標を出力せずに曲線半径だけ更新する
                radius = previous_pos['radius'] if input_d[ix]['value'] == 'c' else input_d[ix]['value']
                theta = previous_pos['theta']
            
            previous_pos['distance'] = input_d[ix]['distance']
            previous_pos['x'] = output[-1][0]
            previous_pos['y'] = output[-1][1]
            previous_pos['theta'] = theta
            previous_pos['is_bt'] = True if input_d[ix]['flag']=='bt' else False
            previous_pos['radius'] = radius
        elif(input_d[ix]['key'] == 'turn'): # 現在点がturnか
            if(previous_pos['is_bt']): # 直前点がbegin transitionなら例外送出（緩和曲線中のturn）
                raise RuntimeError('legacy.turn appeared within the transition curve.')
            if(previous_pos['radius']==0.0): # 直線軌道上のturnなら、現在点までの直線軌道を出力
                res = curve_gen.straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                theta = previous_pos['theta']
            else: # 円軌道上なら、現在点までの円軌道を出力
                res, theta = curve_gen.circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                theta += previous_pos['theta']
            radius = previous_pos['radius']
            theta += np.arctan(input_d[ix]['value']) # valueに相当する角度だけ方位角を増減する
            output = np.vstack((output,res+output[-1]))
            
            previous_pos['distance'] = input_d[ix]['distance']
            previous_pos['x'] = output[-1][0]
            previous_pos['y'] = output[-1][1]
            previous_pos['theta'] = theta
            previous_pos['radius'] = radius
        #if(track_coarse[-1][2] != input_d[ix]['distance']):
        #    track_coarse = np.vstack((track_coarse,np.array([output[-1][0],output[-1][1],input_d[ix]['distance']])))
        ix+=1
        
    ax.plot(output[:,0],output[:,1])
    #ax.scatter(output[:,0],output[:,1],marker='+')
    #ax.scatter(track_coarse[:,0],track_coarse[:,1],marker='+')
    #print(track_coarse)
    ax.set_aspect('equal')
    ax.invert_yaxis()


class Mapplot():
    def __init__(self,env):
        self.environment = env
        trackgenerator = tgen.TrackGenerator(self.environment)
        self.environment.owntrack_pos = trackgenerator.generate_owntrack()
        if (len(self.environment.station.position)>0):
            self.station_dist = np.array(list(self.environment.station.position.keys()))
            self.station_pos = self.environment.owntrack_pos[np.isin(self.environment.owntrack_pos[:,0],self.station_dist)]
            self.nostation = False
        else:
            self.nostation = True
    def plane(self, ax_pl):
        ax_pl.plot(self.environment.owntrack_pos[:,1],self.environment.owntrack_pos[:,2])
        ax_pl.set_aspect('equal')
        ax_pl.invert_yaxis()
    def vertical(self, ax_h, ax_r):
        ax_h.plot(self.environment.owntrack_pos[:,0],self.environment.owntrack_pos[:,3])
        ax_r.plot(self.environment.owntrack_pos[:,0],np.sign(self.environment.owntrack_pos[:,5]))

    def stationpoint_plane(self, ax_pl, labelplot = True):
        if(not self.nostation):
            ax_pl.scatter(self.station_pos[:,1],self.station_pos[:,2], facecolor='white', edgecolors='black', zorder=10)
            
            if(labelplot):
                for i in range(0,len(self.station_pos)):
                    #ax_pl.annotate(environment.station.stationkey[environment.station.position[station_pos[i][0]]],xy=(station_pos[i][1],station_pos[i][2]), zorder=11)
                    ax_pl.text(self.station_pos[i][1],self.station_pos[i][2], self.environment.station.stationkey[self.environment.station.position[self.station_pos[i][0]]], rotation=30, size=8)
    def stationpoint_height(self, ax_h, labelplot = True):
        if(not self.nostation):
            height_max = max(self.station_pos[:,3]) #max(environment.owntrack_pos[:,3])
            height_min = min(self.station_pos[:,3]) #min(environment.owntrack_pos[:,3])
            
            station_marker_ypos = (height_max-height_min)*1.2+height_min
            
            for i in range(0,len(self.station_pos)):
                ax_h.plot([self.station_pos[i][0],self.station_pos[i][0]],[self.station_pos[i][3],station_marker_ypos],color='tab:blue')
                ax_h.scatter(self.station_pos[i][0],station_marker_ypos, facecolor='white', edgecolors='black', zorder=10)
                if(labelplot):
                    ax_h.text(self.station_pos[i][0],station_marker_ypos, self.environment.station.stationkey[self.environment.station.position[self.station_pos[i][0]]], rotation=45, size=8)
    def gradient_value(self, ax_h):
        gradp = tgen.TrackPointer(self.environment, 'gradient')
        grad_last = 0
        height_max = max(self.environment.owntrack_pos[:,3])
        height_min = min(self.environment.owntrack_pos[:,3])
        gradline_min = height_min - (height_max-height_min)*0.05
        while gradp.pointer['next'] != None:
            pos_temp = self.environment.owntrack_pos[self.environment.owntrack_pos[:,0] == gradp.data[gradp.pointer['next']]['distance']][0]
            #if(gradp.data[gradp.pointer['next']]['value'] == 'c'):
            #    ax_h.plot([pos_temp[0],pos_temp[0]],[height_min,pos_temp[3]],color='tab:blue')
            ax_h.plot([pos_temp[0],pos_temp[0]],[gradline_min,pos_temp[3]],color='tab:blue')
            gradp.seeknext()
