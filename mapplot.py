import numpy as np

def gradient_straight(L, gr):
    '''一定勾配に対する高度変化を返す。
    L: 勾配長 [m]
    gr: 勾配 [‰]
    '''
    theta = np.arctan(gr/1000)
    return np.array([L,L*np.sin(theta)]).T

def gradient_transition(L, gr1, gr2, y0=0, n=5):
    '''縦曲線に対する高度変化を返す。
    L: 勾配長 [m]
    gr1: 始点の勾配 [‰]
    gr2: 終点の勾配 [‰]。
    '''
    dist = np.linspace(0,L,n)
    theta1 = np.arctan(gr1/1000)
    theta2 = np.arctan(gr2/1000)
    return np.vstack((dist,y0+L/(theta2-theta1)*np.cos(theta1)-L/(theta2-theta1)*np.cos((theta2-theta1)/L*dist+theta1))).T
    
def clothoid_dist(A, l, elem):
    '''クロソイド曲線の座標を返す。
    A: クロソイドパラメータ
    l: 弧長 [m]
    elem: 求める座標成分 'X'/'Y'
    '''
    if elem == 'X':
        return l*(1-1/40*(l/A)**4+1/3456*(l/A)**8-1/599040*(l/A)**12)
    else:
        return l*(1/6*(l/A)**2-1/336*(l/A)**6+1/42240*(l/A)**10-1/9676800*(l/A)**14)
    
def rotate(tau1):
    '''２次元回転行列を返す。
    tau1: 回転角度 [rad]
    '''
    return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])

def straight(L, theta, l_intermediate = None):
    '''直線軌道の平面座標を返す。
    L: 直線長さ [m]
    theta: 始点での軌道方位角 [rad]
    '''
    dist = L if l_intermediate == None else l_intermediate
    res=np.array([dist,0]).T
    return np.dot(rotate(theta), res).T

def circular_curve(L, R, theta, n=10, l_intermediate = None):
    '''円軌道の平面座標を返す。
    L: 軌道長さ [m]
    R: 曲線半径 [m]
    theta: 始点での軌道方位角 [rad]
    n: 中間点の分割数
    '''
    if(l_intermediate == None):
        dist = np.linspace(0,L,n)
    else:
        dist = l_intermediate
    res = [np.fabs(R)*np.sin(dist/np.fabs(R)),R*(1-np.cos(dist/np.fabs(R)))]
    tau = L/R
    return np.dot(rotate(theta), res).T, tau

def transition_linear(L, r1, r2, theta, n=5, l_intermediate = None):
    '''緩和曲線(直線逓減)の平面座標を返す。
    L: 軌道長さ [m]
    r1: 始点の曲線半径 [m]
    r2: 終点の曲線半径 [m]
    theta: 始点での軌道方位角 [rad]
    n: 中間点の分割数
    '''
    r1 = np.inf if r1==0 else r1
    r2 = np.inf if r2==0 else r2

    L0 = L*(1-(1/(1-(r2)/(r1)))) #曲率が0となる距離。始終点の曲率が同符号の場合はL0<0 or L0>L、異符号の場合は0<L0<Lとなる。

    if(r1 != np.inf):
        A = np.sqrt(np.fabs(L0)*np.fabs(r1))
    else:
        A = np.sqrt(np.fabs(L-L0)*np.fabs(r2))

    if (1/r1 < 1/r2):
        if(l_intermediate == None):
            dist = np.linspace(A**2/r1,A**2/r2,n)
        else:
            dist = np.array([0,l_intermediate])+A**2/r1
        result=np.vstack((clothoid_dist(A,dist,'X'),clothoid_dist(A,dist,'Y'))).T
        tau1 = (A/r1)**2/2 #緩和曲線始端の方位角
        turn = ((L-L0)**2-L0**2)/(2*A**2) #緩和曲線通過前後での方位角変化
    else:
        if(l_intermediate == None):
            dist = np.linspace(-A**2/r1,-A**2/r2,n)
        else:
            dist = np.array([0,l_intermediate])+(-A**2/r1)
        result=np.vstack((clothoid_dist(A,dist,'X'),clothoid_dist(A,dist,'Y')*(-1))).T
        tau1 = -(A/r1)**2/2
        turn = -((L-L0)**2-L0**2)/(2*A**2) #緩和曲線通過前後での方位角変化
    
    return np.dot(rotate(theta), np.dot(rotate(-tau1),(result-result[0]).T)).T, turn

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
    output_gradient = np.array([0,0])
    output_radius = np.array([0,0])
    while (ix < len(input_d)):
        #from IPython.core.debugger import Pdb; Pdb().set_trace()
        if(input_d[ix]['key'] == 'gradient'):
            if (input_d[ix]['value']=='c'):
                res = gradient_straight(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'])
                gradient = previous_pos_gradient['gradient']
            else:
                if(previous_pos_gradient['is_bt']):
                    res = gradient_transition(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'],input_d[ix]['value'])
                else:
                    res = gradient_straight(input_d[ix]['distance']-previous_pos_gradient['distance'],previous_pos_gradient['gradient'])
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
                new_radius = np.sign(input_d[ix]['value'])
                if(previous_pos_radius['is_bt']):
                    result = np.array([input_d[ix]['distance'],new_radius])
                else:
                    result = np.vstack((np.array([input_d[ix]['distance'],previous_pos_radius['radius']]),np.array([input_d[ix]['distance'],new_radius])))
            
            output_radius = np.vstack((output_radius,result))
            
            previous_pos_radius['distance'] = input_d[ix]['distance']
            previous_pos_radius['y']        = output_radius[-1][1]
            previous_pos_radius['is_bt']    = True if input_d[ix]['flag']=='bt' else False
            previous_pos_radius['radius']   = new_radius
        ix+=1
    
    ax_g.plot(output_gradient[:,0],output_gradient[:,1])
    ax_r.plot(output_radius[:,0],output_radius[:,1])
    #ax.scatter(output[:,0],output[:,1],marker='+')


def plot_planer_map(environment, ax):
    '''線路平面図を作成する。
    environment: Environmentオブジェクト
    ax: 描画結果を格納するaxesオブジェクト
    '''
    input_d = environment.own_track.data
    previous_pos = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'radius':0}
    ix = 0
    output = np.array([[0,0]])
    #track_coarse = np.array([[0,0,0]])
    while (ix < len(input_d)):
        #from IPython.core.debugger import Pdb; Pdb().set_trace()
        if(input_d[ix]['key'] == 'radius'):
            if (input_d[ix]['value']=='c'):
                if(previous_pos['radius']==0):
                    res = straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                    theta = previous_pos['theta']
                else:
                    res, theta = circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                    theta += previous_pos['theta']
                radius = previous_pos['radius']
            else:
                if(previous_pos['is_bt']):
                    if(previous_pos['radius'] != input_d[ix]['value']):
                        res, theta = transition_linear(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],input_d[ix]['value'],previous_pos['theta'])
                        theta += previous_pos['theta']
                    elif(input_d[ix]['value'] != 0): #曲線半径が変化しないTransition（カントのみ変化するような場合）
                        res, theta = circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                        theta += previous_pos['theta']
                    else:
                        res = straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                        theta = previous_pos['theta']
                else:
                    if(previous_pos['radius']==0): #曲線半径が0のままのTransition
                        res = straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                        theta = previous_pos['theta']
                    else:
                        res, theta = circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                        theta += previous_pos['theta']
                radius = input_d[ix]['value']
            
            output = np.vstack((output,res+output[-1]))
            
            previous_pos['distance'] = input_d[ix]['distance']
            previous_pos['x'] = output[-1][0]
            previous_pos['y'] = output[-1][1]
            previous_pos['theta'] = theta
            previous_pos['is_bt'] = True if input_d[ix]['flag']=='bt' else False
            previous_pos['radius'] = radius
        elif(input_d[ix]['key'] == 'turn'):
            if(previous_pos['is_bt']):
                raise
            if(previous_pos['radius']==0.0):
                res = straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['theta'])
                theta = previous_pos['theta']
            else:
                res, theta = circular_curve(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],previous_pos['theta'])
                theta += previous_pos['theta']
            radius = previous_pos['radius']
            theta += np.arctan(input_d[ix]['value'])
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
