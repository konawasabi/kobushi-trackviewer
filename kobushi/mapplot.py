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
from . import trackcoordinate as tc
from . import trackgenerator as tgen
import matplotlib.transforms
import pdb


class Mapplot():
    def __init__(self,env,cp_arbdistribution=None,unitdist_default=None):
        if False:
            pdb.set_trace()
        self.environment = env
        self.environment.cp_arbdistribution = cp_arbdistribution
        self.environment.cp_defaultrange = [0,0]
        
        trackgenerator = tgen.TrackGenerator(self.environment,unitdist_default=unitdist_default)
        self.environment.owntrack_pos = trackgenerator.generate_owntrack()
        self.environment.owntrack_curve = trackgenerator.generate_curveradius_dist()
        
        otgenerator = {}
        self.environment.othertrack_pos = {}
        for key in self.environment.othertrack.data.keys():
            otgenerator[key] = tgen.OtherTrackGenerator(self.environment,key)
            self.environment.othertrack_pos[key] = otgenerator[key].generate()
            
        self.distrange = {}
        self.distrange['plane'] = [min(self.environment.owntrack_pos[:,0]),max(self.environment.owntrack_pos[:,0])]
        self.distrange['vertical'] = [min(self.environment.owntrack_pos[:,0]),max(self.environment.owntrack_pos[:,0])]
        self.origin_angle = self.environment.owntrack_pos[self.environment.owntrack_pos[:,0] == min(self.environment.owntrack_pos[:,0])][0][4]
        if (len(self.environment.station.position)>0):
            self.station_dist = np.array(list(self.environment.station.position.keys()))
            self.station_pos = self.environment.owntrack_pos[np.isin(self.environment.owntrack_pos[:,0],self.station_dist)]
            self.nostation = False
        else:
            self.nostation = True
    def plane(self, ax_pl, distmin = None, distmax = None, iswholemap = True, othertrack_list = None, ydim_expansion = None, ydim_offset=0):
        owntrack = self.environment.owntrack_pos
        if (distmin != None):
            self.distrange['plane'][0] = distmin
        if (distmax != None):
            self.distrange['plane'][1] = distmax
        # 描画区間の自軌道データを取り出す
        owntrack = owntrack[owntrack[:,0] >= self.distrange['plane'][0]]
        owntrack = owntrack[owntrack[:,0] <= self.distrange['plane'][1]]
        # 始点での方位角に合わせて回転
        self.origin_angle = owntrack[owntrack[:,0] == min(owntrack[:,0])][0][4]
        owntrack = self.rotate_track(owntrack,-self.origin_angle)
        
        ax_pl.plot(owntrack[:,1],owntrack[:,2],color='black') # 自軌道描画
        
        # 他軌道描画
        if othertrack_list != None:
            for key in othertrack_list:
                othertrack = self.environment.othertrack_pos[key]
                othertrack = othertrack[othertrack[:,0] >= self.environment.othertrack.cp_range[key]['min']]
                othertrack = othertrack[othertrack[:,0] <= self.environment.othertrack.cp_range[key]['max']]
                othertrack = othertrack[othertrack[:,0] >= self.distrange['plane'][0]]
                othertrack = othertrack[othertrack[:,0] <= self.distrange['plane'][1]]
                othertrack = self.rotate_track(othertrack,-self.origin_angle)
                ax_pl.plot(othertrack[:,1],othertrack[:,2],color=self.environment.othertrack_linecolor[key]['current'])
                
        if iswholemap:
            ax_pl.set_aspect('equal') # 全区間表示の場合は、アスペクト比1:1でオートレンジ設定
        else:
            ax_pl.set_aspect('auto')
            windowratio =ax_pl.bbox.height/ax_pl.bbox.width # 平面図のアスペクト比を取得
            plotdistance = max(owntrack[:,0]) - min(owntrack[:,0]) # 描画距離を算出
            # 描画範囲始点の座標を求める
            yminval = owntrack[0][2]
            xminval = owntrack[0][1]
            # 描画範囲設定
            ax_pl.set_ylim(yminval-plotdistance*windowratio/(2*ydim_expansion)+ydim_offset,yminval + plotdistance*windowratio/(2*ydim_expansion)+ydim_offset)
            ax_pl.set_xlim(xminval,xminval + plotdistance)
            
        ax_pl.invert_yaxis()
    def vertical(self, ax_h, ax_r, distmin = None, distmax = None, othertrack_list = None, ylim = None):
        owntrack = self.environment.owntrack_pos
        owntrack_curve = self.environment.owntrack_curve
        if (distmin != None):
            self.distrange['vertical'][0] = distmin
        if (distmax != None):
            self.distrange['vertical'][1] = distmax
        
        
        ot_ix = np.where((owntrack[:,0] >= self.distrange['vertical'][0])&(owntrack[:,0] <= self.distrange['vertical'][1]))[0]
        if len(ot_ix) == 0:
            ot_ix_min = max(np.where((owntrack[:,0] < self.distrange['vertical'][0]))[0])
            ot_ix_max = min(np.where((owntrack[:,0] > self.distrange['vertical'][1]))[0])
        else:
            ot_ix_min = min(ot_ix)
            ot_ix_max = max(ot_ix)
        #print(ot_ix_min,ot_ix_max,owntrack[ot_ix_min],owntrack[ot_ix_max])
        owntrack = owntrack[ot_ix_min:ot_ix_max]
        
        '''
        otc_ix = np.where((owntrack_curve[:,0] >= self.distrange['vertical'][0])&(owntrack_curve[:,0] <= self.distrange['vertical'][1]))[0]
        if len(otc_ix) == 0:
            otc_ix_min = max(np.where((owntrack_curve[:,0] < self.distrange['vertical'][0]))[0])-1
            otc_ix_max = min(np.where((owntrack_curve[:,0] > self.distrange['vertical'][1]))[0])+1
        else:
            otc_ix_min = min(otc_ix)
            otc_ix_max = max(otc_ix)
        owntrack_curve = owntrack_curve[otc_ix_min:otc_ix_max]
        '''
        # 他軌道描画
        if othertrack_list != None:
            for key in othertrack_list:
                othertrack = self.environment.othertrack_pos[key]
                othertrack = othertrack[othertrack[:,0] >= self.environment.othertrack.cp_range[key]['min']]
                othertrack = othertrack[othertrack[:,0] <= self.environment.othertrack.cp_range[key]['max']]
                othertrack = othertrack[othertrack[:,0] >= self.distrange['plane'][0]]
                othertrack = othertrack[othertrack[:,0] <= self.distrange['plane'][1]]
                othertrack = self.rotate_track(othertrack,-self.origin_angle)
                ax_h.plot(othertrack[:,0],othertrack[:,3],color=self.environment.othertrack_linecolor[key]['current'])
        
        self.heightmax = max(owntrack[:,3])
        self.heightmin = min(owntrack[:,3])
        ax_h.plot(owntrack[:,0],owntrack[:,3],color='black')
        ax_r.plot(owntrack_curve[:,0],np.sign(owntrack_curve[:,1]),lw=1,color='black')
        
        ax_r.set_ylim(-6.5,6.5)
        if ylim == None:
            if (self.heightmax - self.heightmin) != 0:
                ax_h.set_ylim(self.heightmin - (self.heightmax - self.heightmin)*0.2,self.heightmax + (self.heightmax - self.heightmin)*0.1)
            else:
                ax_h.set_ylim()
        else:
            ax_h.set_ylim(ylim[0],ylim[1])
            
        ax_h.set_xlim(self.distrange['vertical'][0],self.distrange['vertical'][1])
        ax_r.set_xlim(self.distrange['vertical'][0],self.distrange['vertical'][1])

    def stationpoint_plane(self, ax_pl, labelplot = True):
        if(not self.nostation):
            stationpos = self.station_pos
            stationpos = stationpos[stationpos[:,0] >= self.distrange['plane'][0]]
            stationpos = stationpos[stationpos[:,0] <= self.distrange['plane'][1]]
            
            stationpos = self.rotate_track(stationpos,-self.origin_angle)
            
            if(len(stationpos)>0):
                ax_pl.scatter(stationpos[:,1],stationpos[:,2], facecolor='white', edgecolors='black', zorder=10)
                trans_offs = matplotlib.transforms.offset_copy(ax_pl.transData, x=8*1.2 ,y=8*1, units='dots')
                
                if(labelplot):
                    for i in range(0,len(stationpos)):
                        #ax_pl.annotate(environment.station.stationkey[environment.station.position[station_pos[i][0]]],xy=(station_pos[i][1],station_pos[i][2]), zorder=11)
                        ax_pl.text(stationpos[i][1],stationpos[i][2], self.environment.station.stationkey[self.environment.station.position[stationpos[i][0]]], rotation=0, size=8,bbox=dict(boxstyle="square",ec='black',fc='white',), transform=trans_offs)
    def stationpoint_height(self, ax_h, ax_s, labelplot = True):
        if(not self.nostation):
            stationpos = self.station_pos
            stationpos = stationpos[stationpos[:,0] >= self.distrange['vertical'][0]]
            stationpos = stationpos[stationpos[:,0] <= self.distrange['vertical'][1]]
            
            if(len(stationpos)>0):
                height_max = max(stationpos[:,3])
                height_min = min(stationpos[:,3])
                
                #station_marker_ypos = (height_max-height_min)*1.1+height_min
                station_marker_ypos = self.heightmax
                trans_offs = matplotlib.transforms.offset_copy(ax_s.transData, x=-8/2,y=8*1, units='dots')
                for i in range(0,len(stationpos)):
                    ax_h.plot([stationpos[i][0],stationpos[i][0]],[stationpos[i][3],station_marker_ypos],color='black',lw=1)
                    #ax_h.scatter(self.station_pos[i][0],station_marker_ypos, facecolor='white', edgecolors='black', zorder=10)
                    if(labelplot):
                        #ax_h.text(stationpos[i][0],station_marker_ypos, self.environment.station.stationkey[self.environment.station.position[stationpos[i][0]]], rotation=90, size=8,bbox=dict(boxstyle="square",ec='black',fc='white',), transform=trans_offs)
                        ax_s.text(stationpos[i][0],0, self.environment.station.stationkey[self.environment.station.position[stationpos[i][0]]], rotation=90, size=8,bbox=dict(boxstyle="square",ec='black',fc='white',), transform=trans_offs)
    def gradient_value(self, ax_h, labelplot = True):
        '''縦断面図へ勾配数値をプロットする
        '''
        def vertline():
            # 勾配変化点へ垂直線を描画
            pos_temp = owntrack[owntrack[:,0] == gradient_p.data[gradient_p.pointer['next']]['distance']][0]
            ax_h.plot([pos_temp[0],pos_temp[0]],[gradline_min,pos_temp[3]],color='black',lw=1)
        def gradval(pos_start=None, pos_end=None, value=None, doplot=labelplot):
            # 勾配数値をプロット
            if(doplot):
                if(pos_end == None):
                    pos_end = gradient_p.data[gradient_p.pointer['next']]['distance']
                if(pos_start == None):
                    pos_start = gradient_p.data[gradient_p.pointer['last']]['distance']
                if(value == None):
                    valuecontain = gradient_p.seekoriginofcontinuous(gradient_p.pointer['last'])
                    if valuecontain != None:
                        value = gradient_p.data[valuecontain]['value']
                    else:
                        value = 0
                value = str(np.fabs(value)) if value != 0 else 'Lv.'
                if (pos_start+pos_end)/2 > self.distrange['vertical'][0] and (pos_start+pos_end)/2 < self.distrange['vertical'][1]:
                    ax_h.text((pos_start+pos_end)/2,gradline_min, value, rotation=90, size=6.5, transform=trans_offs)
            
        owntrack = self.environment.owntrack_pos
        owntrack = owntrack[owntrack[:,0] >= self.distrange['vertical'][0]]
        owntrack = owntrack[owntrack[:,0] <= self.distrange['vertical'][1]]
        
        gradient_p = tgen.TrackPointer(self.environment, 'gradient')
        grad_last = 0
        height_max = max(owntrack[:,3])
        height_min = min(owntrack[:,3])
        gradline_min = height_min - (height_max-height_min)*0.1
        trans_offs = matplotlib.transforms.offset_copy(ax_h.transData, x=-8/2, units='dots')
        
        if(gradient_p.pointer['last'] == None and gradient_p.pointer['next'] != None): # 勾配要素が存在するかどうか判断
            while gradient_p.pointer['next'] != None:
                if (gradient_p.data[gradient_p.pointer['next']]['distance'] < self.distrange['vertical'][0]): # プロットする距離程範囲の下限までポインタを進める
                    gradient_p.seeknext()
                else:
                    break
            
            while(gradient_p.pointer['next'] != None and gradient_p.data[gradient_p.pointer['next']]['distance'] <= self.distrange['vertical'][1]):
                # 勾配区切り線の描画処理。変化開始点に描く。
                if(gradient_p.pointer['last'] == None):
                    vertline()
                    gradval(pos_start = min(owntrack[:,0]),value=0)
                else:
                    if(gradient_p.data[gradient_p.pointer['next']]['flag'] == 'bt'):
                        vertline()
                        gradval()
                    elif(gradient_p.data[gradient_p.pointer['next']]['flag'] == 'i'):
                        if(gradient_p.data[gradient_p.seekoriginofcontinuous(gradient_p.pointer['next'])]['value'] == gradient_p.data[gradient_p.pointer['last']]['value']):
                            vertline()
                            gradval()
                    elif(gradient_p.data[gradient_p.pointer['next']]['flag'] == ''):
                        if(gradient_p.data[gradient_p.pointer['last']]['flag'] != 'bt'):
                            vertline()
                            gradval()
                gradient_p.seeknext()
        # 最終勾配制御点以降の勾配値をプロットする
        if(gradient_p.pointer['last'] == None):
            gradval(pos_end = max(owntrack[:,0]),pos_start = min(owntrack[:,0]),value=0)
        else:
            gradval(pos_end = max(owntrack[:,0]))
    def radius_value(self, ax_r, labelplot = True):
        '''縦断面図へ曲線半径をプロットする
        '''
        def pltval(pos_start=None, pos_end=None, value=None, doplot=labelplot):
            if(doplot):
                if(pos_end == None):
                    pos_end = rad_p.data[rad_p.pointer['next']]['distance']
                if(pos_start == None):
                    pos_start = rad_p.data[rad_p.pointer['last']]['distance']
                if(value == None):
                    value = rad_p.data[rad_p.seekoriginofcontinuous(rad_p.pointer['last'])]['value']
                if(value != 0):
                    if (pos_start+pos_end)/2 > self.distrange['vertical'][0] and (pos_start+pos_end)/2 < self.distrange['vertical'][1]:
                        ax_r.text((pos_start+pos_end)/2,1.2*np.sign(value), '{:.0f}'.format(np.fabs(value)), rotation=90, size=6.5, transform=trans_offs, va='bottom' if np.sign(value) > 0 else 'top')
        
        owntrack = self.environment.owntrack_pos
        owntrack = owntrack[owntrack[:,0] >= self.distrange['vertical'][0]]
        owntrack = owntrack[owntrack[:,0] <= self.distrange['vertical'][1]]
        
        rad_p = tgen.TrackPointer(self.environment, 'radius')
        trans_offs = matplotlib.transforms.offset_copy(ax_r.transData, x=-8/2, units='dots')
        
        while rad_p.pointer['next'] != None:
            if(rad_p.data[rad_p.pointer['next']]['distance'] < self.distrange['vertical'][0]):
                rad_p.seeknext()
            else:
                break
        while(rad_p.pointer['next'] != None and rad_p.data[rad_p.pointer['next']]['distance'] <= self.distrange['vertical'][1]):
            if(rad_p.pointer['last'] == None):
                pass
            else:
                if(rad_p.data[rad_p.pointer['next']]['flag'] == 'bt'):
                    pltval()
                elif(rad_p.data[rad_p.pointer['next']]['flag'] == 'i'):
                    if(rad_p.data[rad_p.seekoriginofcontinuous(rad_p.pointer['next'])]['value'] == rad_p.data[rad_p.pointer['last']]['value']):
                        pltval()
                elif(rad_p.data[rad_p.pointer['next']]['flag'] == ''):
                    if(rad_p.data[rad_p.pointer['last']]['flag'] != 'bt'):
                        pltval()
            rad_p.seeknext()
    def rotate_track(self, input, angle):
        def rotate(tau1):
            '''２次元回転行列を返す。
            tau1: 回転角度 [rad]
            '''
            return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])
        temp_i = input.T
        temp_rot = np.dot(rotate(angle),np.vstack((temp_i[1],temp_i[2])))
        return np.vstack((np.vstack((temp_i[0],temp_rot)),temp_i[3:])).T
