'''
    Copyright 2021 konawasabi

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
import numpy as np
from scipy import integrate

class gradient():
    def __init__(self):
        pass
    def straight(self, L, gr):
        '''一定勾配に対する高度変化を返す。
        L: 勾配長 [m]
        gr: 勾配 [‰]
        '''
        dist = L
        theta = np.arctan(gr/1000)
        return np.array([dist,dist*np.sin(theta)]).T
    def transition(self, L, gr1, gr2, y0=0, n=5):
        '''縦曲線に対する高度変化を返す。
        L: 勾配長 [m]
        gr1: 始点の勾配 [‰]
        gr2: 終点の勾配 [‰]。
        '''
        dist = np.linspace(0,L,n)
        theta1 = np.arctan(gr1/1000)
        theta2 = np.arctan(gr2/1000)
        return np.vstack((dist,y0+L/(theta2-theta1)*np.cos(theta1)-L/(theta2-theta1)*np.cos((theta2-theta1)/L*dist+theta1))).T
        
class gradient_intermediate(gradient):
    def __init__(self):
        pass
    def straight(self, L, gr, l_intermediate):
        '''全長Lの一定勾配について、l_intermediateでの高度変化を返す。
        L: 勾配長 [m]
        gr: 勾配 [‰]
        '''
        dist = l_intermediate
        theta = np.arctan(gr/1000)
        return np.array([dist,dist*np.sin(theta)]).T[-1]
    def transition(self, L, gr1, gr2, l_intermediate, y0=0):
        '''全長Lの縦曲線について、l_intermediateでの高度変化、勾配を返す。
        L: 縦曲線長 [m]
        gr1: 始点の勾配 [‰]
        gr2: 終点の勾配 [‰]。
        '''
        dist = l_intermediate
        theta1 = np.arctan(gr1/1000)
        theta2 = np.arctan(gr2/1000)
        return np.vstack((dist,y0+L/(theta2-theta1)*np.cos(theta1)-L/(theta2-theta1)*np.cos((theta2-theta1)/L*dist+theta1))).T[-1], 1000*np.tan((theta2 - theta1)/L*l_intermediate + theta1)
    
class curve():
    def __init__(self):
        pass
    def clothoid_dist(self, A, l, elem):
        '''クロソイド曲線の座標を返す。
        A: クロソイドパラメータ
        l: 弧長 [m]
        elem: 求める座標成分 'X'/'Y'
        '''
        if elem == 'X':
            return l*(1-1/40*(l/A)**4+1/3456*(l/A)**8-1/599040*(l/A)**12)
        else:
            return l*(1/6*(l/A)**2-1/336*(l/A)**6+1/42240*(l/A)**10-1/9676800*(l/A)**14)
        
    def rotate(self, tau1):
        '''２次元回転行列を返す。
        tau1: 回転角度 [rad]
        '''
        return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])

    def straight(self, L, theta):
        '''直線軌道の平面座標を返す。
        L: 直線長さ [m]
        theta: 始点での軌道方位角 [rad]
        '''
        dist = L
        res=np.array([dist,0]).T
        return np.dot(self.rotate(theta), res).T

    def circular_curve(self, L, R, theta, n=10):
        '''円軌道の平面座標を返す。
        L: 軌道長さ [m]
        R: 曲線半径 [m]
        theta: 始点での軌道方位角 [rad]
        n: 中間点の分割数
        '''
        dist = np.linspace(0,L,n)
        tau = L/R
        res = [np.fabs(R)*np.sin(dist/np.fabs(R)),R*(1-np.cos(dist/np.fabs(R)))]
        return (np.dot(self.rotate(theta), res).T)[1:], tau

    def transition_curve(self, L, r1, r2, theta, func, n=5):
        '''緩和曲線の平面座標を返す。
        L: 軌道長さ [m]
        r1: 始点の曲線半径 [m]
        r2: 終点の曲線半径 [m]
        theta: 始点での軌道方位角 [rad]
        func: 逓減関数('line': 直線逓減, 'sin':sin半波長逓減)
        n: 中間点の分割数
        '''
        r1 = np.inf if r1==0 else r1
        r2 = np.inf if r2==0 else r2

        if func == 'line': # 直線逓減の場合
            L0 = L*(1-(1/(1-(r2)/(r1)))) #曲率が0となる距離。始終点の曲率が同符号の場合はL0<0 or L0>L、異符号の場合は0<L0<Lとなる。
            
            # クロソイドパラメータAの決定
            if(r1 != np.inf):
                A = np.sqrt(np.fabs(L0)*np.fabs(r1))
            else:
                A = np.sqrt(np.fabs(L-L0)*np.fabs(r2))

            if (1/r1 < 1/r2): # 右向きに曲率が増加する場合
                tau1 = (A/r1)**2/2 #緩和曲線始端の方位角
                dist = np.linspace(A**2/r1,A**2/r2,n)
                turn = ((L-L0)**2-L0**2)/(2*A**2) #緩和曲線通過前後での方位角変化。クロソイド曲線の接線角τは、原点(L0)からの距離lに対してτ=l^2/(2A^2)。
                result=np.vstack((self.clothoid_dist(A,dist,'X'),self.clothoid_dist(A,dist,'Y'))).T
            else: # 左向きに曲率が増加する場合
                tau1 = -(A/r1)**2/2
                dist = np.linspace(-A**2/r1,-A**2/r2,n)
                turn = -((L-L0)**2-L0**2)/(2*A**2) #緩和曲線通過前後での方位角変化
                result=np.vstack((self.clothoid_dist(A,dist,'X'),self.clothoid_dist(A,dist,'Y')*(-1))).T
        elif func == 'sin':
            output = self.harfsin_intermediate(L, r1, r2, L)
            tau1 = 0
            turn = output[2]
            rl = output[3] #if output[3] != 0 else np.inf

            result_temp = np.vstack((output[0],output[1])).T
            result = result_temp[::int(np.ceil(len(output[0])/n))]
            result = np.vstack((result,result_temp[-1]))
        else:
            raise RuntimeError('invalid transition function')
        
        return (np.dot(self.rotate(theta), np.dot(self.rotate(-tau1),(result-result[0]).T)).T)[1:], turn
    def harfsin_intermediate(self, L, r1, r2, l_intermediate, dL=1):
        def K(x,R1,R2,L):
            '''sin半波長逓減の緩和曲線に対する曲率を返す。
            x: 始点からの距離
            R1: 始点での曲率半径
            R2: 終点での曲率半径
            L: 緩和曲線の全長
            '''
            return (1/R2-1/R1)/2*(np.sin(np.pi/L*x-np.pi/2)+1)+1/R1
        if l_intermediate > 0:
            if l_intermediate/5 <= dL:
                dL = l_intermediate/5
            tau_X = np.linspace(0,l_intermediate,int((l_intermediate)/dL)+1)
            tau = integrate.cumtrapz(K(tau_X,r1,r2,L),tau_X,initial = 0)
            X = integrate.cumtrapz(np.cos(tau),tau_X,initial = 0)
            Y = integrate.cumtrapz(np.sin(tau),tau_X,initial = 0)
            r_interm = 1/K(l_intermediate,r1,r2,L) if K(l_intermediate,r1,r2,L) != 0 else np.inf
        else:
            X = 0
            Y = 0
            tau = np.array([0])
            r_interm = r1 if r1 != 0 else np.inf
        return (X,Y,tau[-1],r_interm)
        
class curve_intermediate(curve):
    def straight(self,L, theta, l_intermediate):
        '''直線軌道の平面座標を返す。
        L: 直線長さ [m]
        theta: 始点での軌道方位角 [rad]
        l_intermediate: 座標を出力する原点からの距離
        '''
        dist = l_intermediate
        res=np.array([dist,0]).T
        return np.dot(self.rotate(theta), res).T

    def circular_curve(self,L, R, theta, l_intermediate):
        '''全長Lの円曲線について、l_intermediateでの座標、方位を返す。
        L: 軌道長さ [m]
        R: 曲線半径 [m]
        theta: 始点での軌道方位角 [rad]
        l_intermediate: 座標を出力する原点からの距離
        '''
        dist = np.array([0,l_intermediate])
        tau = l_intermediate/R
        res = [np.fabs(R)*np.sin(dist/np.fabs(R)),R*(1-np.cos(dist/np.fabs(R)))]
        return (np.dot(self.rotate(theta), res).T)[-1], tau

    def transition_curve(self,L, r1, r2, theta, func, l_intermediate):
        '''全長Lの緩和曲線について、l_intermediateでの座標、方位、曲線半径を返す。
        L: 軌道長さ [m]
        r1: 始点の曲線半径 [m]
        r2: 終点の曲線半径 [m]
        theta: 始点での軌道方位角 [rad]
        func: 逓減関数('line': 直線逓減, 'sin':sin半波長逓減)
        l_intermediate: 座標を出力する原点からの距離
        '''
        r1 = np.inf if r1==0 else r1
        r2 = np.inf if r2==0 else r2
        
        r1 = np.inf if np.fabs(r1)>1e6 else r1
        r2 = np.inf if np.fabs(r2)>1e6  else r2

        #print(L, r1, r2, theta, func, l_intermediate)

        if func == 'line': # 直線逓減の場合
            L0 = L*(1-(1/(1-(r2)/(r1)))) #曲率が0となる距離。始終点の曲率が同符号の場合はL0<0 or L0>L、異符号の場合は0<L0<Lとなる。
            rl = 1/(1/r1 + (1/r2 - 1/r1)/L * l_intermediate) if (1/r1 + (1/r2 - 1/r1)/L * l_intermediate) != 0 else np.inf
            
            # クロソイドパラメータAの決定
            if(r1 != np.inf):
                A = np.sqrt(np.fabs(L0)*np.fabs(r1))
            else:
                A = np.sqrt(np.fabs(L-L0)*np.fabs(r2))

            if (1/r1 < 1/r2): # 右向きに曲率が増加する場合
                tau1 = (A/r1)**2/2 #緩和曲線始端の方位角
                dist = np.array([0,l_intermediate])+A**2/r1
                turn = ((l_intermediate-L0)**2-L0**2)/(2*A**2) # 緩和曲線通過前後での方位角変化。クロソイド曲線の接線角τは、原点(L0)からの距離lに対してτ=l^2/(2A^2)。
                result=np.vstack((self.clothoid_dist(A,dist,'X'),self.clothoid_dist(A,dist,'Y'))).T
            else: # 左向きに曲率が増加する場合
                tau1 = -(A/r1)**2/2
                dist = np.array([0,l_intermediate])+(-A**2/r1)
                turn = -((l_intermediate-L0)**2-L0**2)/(2*A**2)
                result=np.vstack((self.clothoid_dist(A,dist,'X'),self.clothoid_dist(A,dist,'Y')*(-1))).T
        elif func == 'sin':
            output = self.harfsin_intermediate(L, r1, r2, l_intermediate)
            tau1 = 0
            turn = output[2]
            rl = output[3] #if output[3] != 0 else np.inf
            result = np.vstack((output[0],output[1])).T
        else:
            raise RuntimeError('invalid transition function')
        return (np.dot(self.rotate(theta), np.dot(self.rotate(-tau1),(result-result[0]).T)).T)[-1], turn, rl if np.fabs(rl) < 1e6 else 0
    def harfsin_intermediate(self, L, r1, r2, l_intermediate, dL=1):
        def K(x,R1,R2,L):
            '''sin半波長逓減の緩和曲線に対する曲率を返す。
            x: 始点からの距離
            R1: 始点での曲率半径
            R2: 終点での曲率半径
            L: 緩和曲線の全長
            '''
            return (1/R2-1/R1)/2*(np.sin(np.pi/L*x-np.pi/2)+1)+1/R1
        if l_intermediate > 0:
            if l_intermediate/5 <= dL:
                dL = l_intermediate/5
            tau_X = np.linspace(0,l_intermediate,int((l_intermediate)/dL)+1)
            tau = integrate.cumtrapz(K(tau_X,r1,r2,L),tau_X,initial = 0)
            X = integrate.cumtrapz(np.cos(tau),tau_X,initial = 0)
            Y = integrate.cumtrapz(np.sin(tau),tau_X,initial = 0)
            r_interm = 1/K(l_intermediate,r1,r2,L) if K(l_intermediate,r1,r2,L) != 0 else np.inf
        else:
            X = 0
            Y = 0
            tau = np.array([0])
            r_interm = r1 if r1 != 0 else np.inf
        return (X,Y,tau[-1],r_interm)
        
class Cant():
    def __init__(self, pointer, data, last_pos):
        self.pointer       = pointer
        self.data_ownt     = data
        self.last_pos      = last_pos
        
        self.cant_lastpos = {}
        self.cant_lastpos['distance'] = 0 #last_pos['distance']
        self.cant_lastpos['value']    = last_pos['cant']
    def process(self, dist, func):
        while (self.pointer.overNextpoint(dist)): #注目している要素区間の終端を超えたか？
            if(self.pointer.seekoriginofcontinuous(self.pointer.pointer['next']) != None):
                self.cant_lastpos['distance'] = self.data_ownt[self.pointer.seekoriginofcontinuous(self.pointer.pointer['next'])]['distance']
                self.cant_lastpos['value']    = self.data_ownt[self.pointer.seekoriginofcontinuous(self.pointer.pointer['next'])]['value']
            self.pointer.seeknext()
        
        result = 0
        if(self.pointer.pointer['last'] == None): #最初の要素に到達していない
            result = self.cant_lastpos['value']
        elif(self.pointer.pointer['next'] == None): #最後の要素を通過した
            result = self.cant_lastpos['value']
        else: # 一般の場合の処理
            if(self.data_ownt[self.pointer.pointer['next']]['value'] == 'c'): # 注目区間の前後でvalueが変化しない場合
                result = self.cant_lastpos['value']
            else:
                if(self.data_ownt[self.pointer.pointer['next']]['flag'] == 'i' or self.data_ownt[self.pointer.pointer['last']]['flag'] == 'bt'): # interpolateフラグがある場合
                    if(self.cant_lastpos['value'] != self.data_ownt[self.pointer.pointer['next']]['value']):
                        result = self.transition(self.data_ownt[self.pointer.pointer['next']]['distance'] - self.data_ownt[self.pointer.pointer['last']]['distance'],\
                                                 self.cant_lastpos['value'],\
                                                 self.data_ownt[self.pointer.pointer['next']]['value'],\
                                                 func,\
                                                 dist - self.data_ownt[self.pointer.pointer['last']]['distance'])
                    else:
                        result = self.cant_lastpos['value']
                else: # interpolateでない場合、lastposのvalueを出力
                    result = self.cant_lastpos['value']
        return result
    def transition(self, L, c1, c2, func, l_intermediate):
        if(func == 'sin'):
            result = (c2-c1)/2*(np.sin(np.pi/L*l_intermediate-np.pi/2)+1)+c1
        else:
            result = (c2-c1)/L*l_intermediate + c1
        return result
        
class OtherTrack():
    def __init__(self):
        pass
    def relative_position(self, L, radius, ya, yb, l_intermediate):
        '''注目点での相対座標を返す。
        L:              区間長
        radius:         相対半径
        ya, yb:         区間始終点での相対位置
        l_intermediate: 座標を求める位置
        '''
        if L == 0:
            Y = yb
        elif radius != 0:
            sintheta = np.sqrt(L**2+(yb-ya)**2)/(2*radius)
            if np.fabs(sintheta) <= 1: # 与えられた相対半径radiusと区間長Lで座標計算できるか判断する
                tau = np.arctan((yb-ya)/L) # 注目する区間の始終点を結ぶ直線が自軌道となす角
                theta = 2*np.arcsin(sintheta) # 注目する区間での方位角の変化

                phiA = theta/2-tau # 区間始点での自軌道に対する方位角
                # 円軌道の中心座標
                x0 = 0 + radius*np.sin(phiA)
                y0 = ya + radius*np.cos(phiA)
                # 注目点の座標
                Y = y0 - radius*np.cos(np.arcsin((l_intermediate-x0)/radius))
            else: # 計算できないradius, Lの場合、直線として計算
                Y = (yb - ya)/L * l_intermediate + ya if L != 0 else 0
        else: # radius==0 なら直線として計算
            Y = (yb - ya)/L * l_intermediate + ya if L != 0 else 0
        
        return Y
    def rotate(self, tau1):
        '''２次元回転行列を返す。
        tau1: 回転角度 [rad]
        '''
        return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])
    def absolute_position_X(self, L, radius, xa, xb, l_intermediate, pos_ownt):
        '''他軌道x方向(水平方向)の絶対座標を返す
        L:              区間長
        radius:         相対半径
        xa, xb:         区間始終点でのx方向位置
        l_intermediate: 座標を求める位置
        pos_ownt:       座標を求める位置での自軌道の座標情報
        '''
        posrel = np.array([0,self.relative_position(L, radius, xa, xb, l_intermediate)])
        return np.dot(self.rotate(pos_ownt[4]),posrel) + np.array([pos_ownt[1],pos_ownt[2]]) # 自軌道の方位角に応じて計算結果を回転させ、自軌道座標に加算する
    def absolute_position_Y(self, L, radius, ya, yb, l_intermediate, pos_ownt):
        '''他軌道y方向(鉛直方向)の絶対座標を返す
        L:              区間長
        radius:         相対半径
        ya, yb:         区間始終点でのy方向位置
        l_intermediate: 座標を求める位置
        pos_ownt:       座標を求める位置での自軌道の座標情報
        '''
        posrel = np.array([0,self.relative_position(L, radius, ya, yb, l_intermediate)])
        return posrel + np.array([pos_ownt[1],pos_ownt[3]]) # 計算結果を自軌道座標に加算する

