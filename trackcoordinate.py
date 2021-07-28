import numpy as np

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

        if True: # 直線逓減の場合
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
        return (np.dot(self.rotate(theta), np.dot(self.rotate(-tau1),(result-result[0]).T)).T)[1:], turn
        
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

        if True: # 直線逓減の場合
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
        return (np.dot(self.rotate(theta), np.dot(self.rotate(-tau1),(result-result[0]).T)).T)[-1], turn, rl if np.fabs(rl) < 1e6 else 0

class OtherTrack():
    def __init__(self):
        pass
    def relative_position(self, L, radius, ya, yb, l_intermediate):
        if radius != 0:
            tau = np.arctan((yb-ya)/L)
            theta = 2*np.arcsin(np.sqrt(L**2+(yb-ya)**2)/(2*radius))

            phiA = theta/2-tau

            x0 = 0 + radius*np.sin(phiA)
            y0 = ya + radius*np.cos(phiA)

            Y = y0 - radius*np.cos(np.arcsin((l_intermediate-x0)/radius))
        else:
            Y = (yb - ya)/L * l_intermediate + ya
        
        return Y
    def rotate(self, tau1):
        '''２次元回転行列を返す。
        tau1: 回転角度 [rad]
        '''
        return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])
    def absolute_position_X(self, L, radius, xa, xb, l_intermediate, pos_ownt):
        '''
        pos_ownt:
        '''
        posrel = np.array([0,self.relative_position(L, radius, xa, xb, l_intermediate)])
        return np.dot(self.rotate(pos_ownt[4]),posrel) + np.array([pos_ownt[1],pos_ownt[2]])
    def absolute_position_Y(self, L, radius, ya, yb, l_intermediate, pos_ownt):
        posrel = np.array([0,self.relative_position(L, radius, ya, yb, l_intermediate)])
        return posrel + np.array([pos_ownt[1],pos_ownt[3]])
