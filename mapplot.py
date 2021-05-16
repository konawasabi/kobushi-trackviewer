import numpy as np

def gradient_straight(L, gr):
    theta = np.arctan(gr/1000)
    return np.array([L,L*np.sin(theta)]).T

def gradient_transition(L, gr1, gr2, y0=0):
    dist = np.linspace(0,L,10)
    theta1 = np.arctan(gr1/1000)
    theta2 = np.arctan(gr2/1000)
    return np.vstack((dist,y0+L/(theta2-theta1)*np.cos(theta1)-L/(theta2-theta1)*np.cos((theta2-theta1)/L*dist+theta1))).T
    
def clothoid_dist(A, l, elem):
    if elem == 'X':
        return l*(1-1/40*(l/A)**4+1/3456*(l/A)**8-1/599040*(l/A)**12)
    else:
        return l*(1/6*(l/A)**2-1/336*(l/A)**6+1/42240*(l/A)**10-1/9676800*(l/A)**14)
    
def rotate(tau1):
    return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])

def straight(L, theta):
    res=np.array([[0,0],[L,0]]).T
    return np.dot(rotate(theta), res).T

def circular_curve(L, R, theta, n=10):
    dist = np.linspace(0,L,n)
    res = [np.fabs(R)*np.sin(dist/np.fabs(R)),R*(1-np.cos(dist/np.fabs(R)))]
    tau = L/R
    return np.dot(rotate(theta), res).T, tau

def transition_linear(L, r1, r2, theta, n=10):
    r1 = np.inf if r1==0 else r1
    r2 = np.inf if r2==0 else r2

    L0 = L*(1-(1/(1-(r2)/(r1))))

    if(r1 != np.inf):
        A = np.sqrt(np.fabs(L0)*np.fabs(r1))
    else:
        A = np.sqrt(np.fabs(L-L0)*np.fabs(r2))

    if (1/r1 < 1/r2):
        dist = np.linspace(A**2/r1,A**2/r2,10)
        result=np.vstack((clothoid_dist(A,dist,'X'),clothoid_dist(A,dist,'Y'))).T
        tau1= -(A/r1)**2/2
    else:
        dist = np.linspace(-A**2/r1,-A**2/r2,10)
        result=np.vstack((clothoid_dist(A,dist,'X'),clothoid_dist(A,dist,'Y')*(-1))).T
        tau1= (A/r1)**2/2
    
    tau2 = (A/r2)**2/2
    
    return np.dot(rotate(theta), np.dot(rotate(tau1),(result-result[0]).T)).T, tau2 - tau1

def plot_vetical_crosssection(input_d, ax):
    previous_pos = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'radius':0, 'gradient':0}
    ix = 0
    output = np.array([0,0])
    while (ix < len(input_d)):
        #from IPython.core.debugger import Pdb; Pdb().set_trace()
        if(input_d[ix]['key'] == 'gradient'):
            if (input_d[ix]['value']=='c'):
                res = gradient_straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['gradient'])
                gradient = previous_pos['gradient']
            else:
                if(previous_pos['is_bt']):
                    res = gradient_transition(input_d[ix]['distance']-previous_pos['distance'],previous_pos['gradient'],input_d[ix]['value'])
                else:
                     res = gradient_straight(input_d[ix]['distance']-previous_pos['distance'],previous_pos['gradient'])
                gradient = input_d[ix]['value']
                
                output = np.vstack((output,res+output[-1]))
                
                previous_pos['distance'] = input_d[ix]['distance']
                previous_pos['y'] = output[-1][1]
                previous_pos['is_bt'] = True if input_d[ix]['flag']=='bt' else False
                previous_pos['gradient'] = gradient
        ix+=1
        
    ax.plot(output[:,0],output[:,1])


def plot_planer_map(input_d, ax):
    previous_pos = {'distance':0, 'x':0, 'y':0, 'theta':0, 'is_bt':False, 'radius':0}
    ix = 0
    output = np.array([0,0])
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
                    res, theta = transition_linear(input_d[ix]['distance']-previous_pos['distance'],previous_pos['radius'],input_d[ix]['value'],previous_pos['theta'])
                    theta += previous_pos['theta']
                else:
                    if(previous_pos['radius']==0):
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
        ix+=1
        
    ax.plot(output[:,0],output[:,1])
    ax.set_aspect('equal')
    ax.invert_yaxis()
