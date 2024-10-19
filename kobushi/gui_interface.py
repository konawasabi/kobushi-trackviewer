'''
    Copyright 2021-2024 konawasabi

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
import sys
import pathlib
import os
import webbrowser
import argparse

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.font as font

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
import matplotlib.gridspec
import matplotlib.font_manager
import numpy as np

# https://qiita.com/yniji/items/3fac25c2ffa316990d0c matplotlibで日本語を使う
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']


from ._version import __version__
from . import mapinterpreter as interp
from . import mapplot
from . import dialog_multifields
from . import othertrack_window
from . import font_window

# http://centerwave-callout.com/tkinter内で起きた例外をどうキャッチするか？/
class Catcher: # tkinter内で起きた例外をキャッチする
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget
    
    def __call__(self, *args):
        try:
            if self.subst:
               args = self.subst(*args)
            return self.func(*args)
        except Exception as e:
            if not __debug__: # デバッグモード(-O)なら素通し。pdbが起動する
                raise e
            else:
                print(e) # 通常モードならダイアログ表示
                tk.messagebox.showinfo(message=e)

class mainwindow(ttk.Frame):
    def __init__(self, master, parser, stepdist = 25, font = ''):
        self.dmin = None
        self.dmax = None
        self.result = None
        self.profYlim = None
        self.default_track_interval = stepdist
        
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Kobushi trackviewer ver. {:s}'.format(__version__))
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        
        master.protocol('WM_DELETE_WINDOW', self.ask_quit)
        
        self.fontctrl = font_window.FontControl(None,self)
        if font != '':
            self.fontctrl.set_fontname(font)
        
        self.create_widgets()
        self.create_menubar()
        self.bind_keyevent()
        self.subwindow = othertrack_window.SubWindow(tk.Toplevel(master), self)
        
        self.parser = parser

    def create_widgets(self):
        # 補助情報フレーム
        self.control_frame = ttk.Frame(self, padding='3 3 3 3')
        self.control_frame.grid(column=1, row=1, sticky=(tk.S))
        
        font_title = font.Font(weight='bold',size=10)
        
        self.ydim_control = ttk.Frame(self.control_frame, padding='3 3 3 3', borderwidth=1, relief='ridge')
        self.ydim_control.grid(column=0, row=0, sticky=(tk.S, tk.W, tk.E))
        self.ydim_cont_label =  ttk.Label(self.ydim_control, text='Y軸拡大率', font = font_title)
        self.ydim_cont_label.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        self.ydim_cont_val = tk.StringVar()
        self.ydim_cont={}
        i=1
        for key in ['x0.5','x1','x2','x4', 'x8', 'x16']:
            self.ydim_cont[key] = ttk.Radiobutton(self.ydim_control, text=key, variable=self.ydim_cont_val, value=key, command=self.plot_all)
            self.ydim_cont[key].grid(column=0, row=i, sticky=(tk.N, tk.W, tk.E))
            i +=1
        self.ydim_cont_val.set('x1')
        self.ydim_offset_label =  ttk.Label(self.ydim_control, text='Y軸オフセット', font = font_title)
        self.ydim_offset_label.grid(column=0, row=10, sticky=(tk.N, tk.W, tk.E))
        self.ydim_offset_val = tk.DoubleVar(value=0)
        self.ydim_offset_entry = ttk.Entry(self.ydim_control, width=6, textvariable=self.ydim_offset_val)
        self.ydim_offset_entry.grid(column=0, row=11, sticky=(tk.W))
        
        self.aux_values_control = ttk.Frame(self.control_frame, padding='3 3 3 3', borderwidth=1, relief='ridge')
        self.aux_values_control.grid(column=0, row=1, sticky=(tk.S, tk.W, tk.E))
        self.aux_val_label =  ttk.Label(self.aux_values_control, text='補助情報', font = font_title)
        self.aux_val_label.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        self.stationpos_val = tk.BooleanVar(value=True)
        self.stationpos_chk = ttk.Checkbutton(self.aux_values_control, text='駅座標',onvalue=True, offvalue=False, variable=self.stationpos_val, command=self.plot_all)
        self.stationpos_chk.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E))
        self.stationlabel_val = tk.BooleanVar(value=True)
        self.stationlabel_chk = ttk.Checkbutton(self.aux_values_control, text='駅名',onvalue=True, offvalue=False, variable=self.stationlabel_val, command=self.plot_all)
        self.stationlabel_chk.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E))
        self.gradientpos_val = tk.BooleanVar(value=True)
        self.gradientpos_chk = ttk.Checkbutton(self.aux_values_control, text='勾配変化点',onvalue=True, offvalue=False, variable=self.gradientpos_val, command=self.plot_all)
        self.gradientpos_chk.grid(column=0, row=3, sticky=(tk.N, tk.W, tk.E))
        self.gradientval_val = tk.BooleanVar(value=True)
        self.gradientval_chk = ttk.Checkbutton(self.aux_values_control, text='勾配値',onvalue=True, offvalue=False, variable=self.gradientval_val, command=self.plot_all)
        self.gradientval_chk.grid(column=0, row=4, sticky=(tk.N, tk.W, tk.E))
        self.curveval_val = tk.BooleanVar(value=True)
        self.curveval_chk = ttk.Checkbutton(self.aux_values_control, text='曲線半径',onvalue=True, offvalue=False, variable=self.curveval_val, command=self.plot_all)
        self.curveval_chk.grid(column=0, row=5, sticky=(tk.N, tk.W, tk.E))
        self.prof_othert_val = tk.BooleanVar(value=False)
        self.prof_othert_chk = ttk.Checkbutton(self.aux_values_control, text='縦断面図他軌道',onvalue=True, offvalue=False, variable=self.prof_othert_val, command=self.plot_all)
        self.prof_othert_chk.grid(column=0, row=6, sticky=(tk.N, tk.W, tk.E))
        
        # 描画区間フレーム
        self.distlimit_control = ttk.Frame(self.control_frame, padding='3 3 3 3', borderwidth=1, relief='ridge')
        self.distlimit_control.grid(column=0, row=2, sticky=(tk.S, tk.W, tk.E))
        self.distlimit_label =  ttk.Label(self.distlimit_control, text='描画区間', font = font_title)
        self.distlimit_label.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        self.dist_range_sel = tk.StringVar(value='all')
        self.dist_range_all = ttk.Radiobutton(self.distlimit_control, text='全範囲',variable=self.dist_range_sel, value='all', command=self.setdist_all)
        self.dist_range_all.grid(column=0, row=1, sticky=(tk.W, tk.E))
        self.dist_range_arb_frame = ttk.Frame(self.distlimit_control, padding='0 0 0 0')
        self.dist_range_arb_frame.grid(column=0, row=2, sticky=(tk.W, tk.E))
        self.dist_range_arb = ttk.Radiobutton(self.dist_range_arb_frame, text='',variable=self.dist_range_sel, value='arb', command=self.setdist_arbitrary)
        self.dist_range_arb.grid(column=0, row=0, sticky=(tk.W, tk.E))
        self.dist_range_arb_val = tk.DoubleVar(value=500)
        self.dist_range_arb_entry = ttk.Entry(self.dist_range_arb_frame, width=5, textvariable=self.dist_range_arb_val)
        self.dist_range_arb_entry.grid(column=1, row=0, sticky=(tk.W))
        self.distlimit_label =  ttk.Label(self.dist_range_arb_frame, text='m')
        self.distlimit_label.grid(column=2, row=0, sticky=(tk.W))
        
        # ファイルパスフレーム
        self.file_frame = ttk.Frame(self, padding='3 3 3 3')
        self.file_frame.grid(column=0, row=0, sticky=(tk.N, tk.W))
        self.open_btn = ttk.Button(self.file_frame, text="開く", command=self.open_mapfile)
        self.open_btn.grid(column=0, row=0, sticky=(tk.W))
        self.filedir_entry_val = tk.StringVar()
        self.filedir_entry = ttk.Entry(self.file_frame, width=75, textvariable=self.filedir_entry_val)
        self.filedir_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.setdist_frame = ttk.Frame(self, padding='3 3 3 3')
        self.setdist_frame.grid(column=0, row=2, sticky=(tk.S, tk.W, tk.E))
        
        self.setdist_entry_frame = ttk.Frame(self.setdist_frame, padding='0 0 0 0')
        self.setdist_entry_frame.grid(column=0, row=0, sticky=(tk.W, tk.E))
        self.distset_btn = ttk.Button(self.setdist_entry_frame, text="距離程セット", command=self.distset_entry, width=12)
        self.distset_btn.grid(column=0, row=0, sticky=(tk.W))
        self.setdist_entry_val = tk.DoubleVar()
        self.setdist_entry = ttk.Entry(self.setdist_entry_frame, width=7, textvariable=self.setdist_entry_val)
        self.setdist_entry.grid(column=1, row=0, sticky=(tk.W))
        self.setdist_entry_label = ttk.Label(self.setdist_entry_frame, text='m')
        self.setdist_entry_label.grid(column=2, row=0, sticky=(tk.W))
        
        # 距離程フレーム
        self.distance_scale = ttk.Scale(self.setdist_frame, orient=tk.HORIZONTAL, from_=0, to=100, command=self.setdist_scale)#,length=500)
        self.distance_scale.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.stationlist_frame = ttk.Frame(self.setdist_frame, padding='0 0 0 0')
        self.stationlist_frame.grid(column=2, row=0, sticky=(tk.E))
        self.stationlist_label = ttk.Label(self.stationlist_frame, text='駅移動', font = font_title)
        self.stationlist_label.grid(column=0, row=0, sticky=(tk.W))
        self.stationlist_val = tk.StringVar()
        self.stationlist_cb = ttk.Combobox(self.stationlist_frame, textvariable=self.stationlist_val, width = 20, state='readonly')
        self.stationlist_cb.grid(column=1, row=0, sticky=(tk.W, tk.E))
        self.stationlist_cb.bind('<<ComboboxSelected>>', self.jumptostation)
        
        self.setdist_frame.columnconfigure(0, weight=0)
        self.setdist_frame.columnconfigure(1, weight=1)
        self.setdist_frame.rowconfigure(0, weight=1)
        
        # プロットフレーム
        self.canvas_frame = ttk.Frame(self, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_plane = plt.figure(figsize=(9,7),tight_layout=True)
        
        gs1 = self.fig_plane.add_gridspec(nrows=2,ncols=1,height_ratios=[22, 13])
        gs2 = gs1[1].subgridspec(nrows=3,ncols=1,height_ratios=[3, 6, 4],hspace=0)
        self.ax_plane = self.fig_plane.add_subplot(gs1[0])
        self.ax_profile_s = self.fig_plane.add_subplot(gs2[0])
        self.ax_profile_g = self.fig_plane.add_subplot(gs2[1], sharex=self.ax_profile_s)
        self.ax_profile_r = self.fig_plane.add_subplot(gs2[2], sharex=self.ax_profile_s)
        
        self.ax_profile_s.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)
        self.ax_profile_g.tick_params(labelbottom=False, bottom=False)
        self.ax_profile_r.tick_params(labelleft=False, left=False)
        
        self.plt_canvas_base = tk.Canvas(self.canvas_frame, bg="white", width=900, height=700)
        self.plt_canvas_base.grid(row = 0, column = 0)
        
        '''
        self.fig_xscroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.plt_canvas_base.xview)
        self.fig_xscroll.grid(row = 1, column = 0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.fig_yscroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.plt_canvas_base.yview)
        self.fig_yscroll.grid(row = 0, column = 1, sticky=(tk.N, tk.W, tk.E, tk.S))
        '''
        def on_canvas_resize(event):
            self.plt_canvas_base.itemconfigure(self.fig_frame_id, width=event.width, height=event.height)
            #print(event)
        
        self.fig_frame = tk.Frame(self.plt_canvas_base)
        self.fig_frame_id = self.plt_canvas_base.create_window((0, 0), window=self.fig_frame, anchor="nw")
        self.fig_frame.columnconfigure(0, weight=1)
        self.fig_frame.rowconfigure(0, weight=1)
        #self.fig_frame.bind("<Configure>",lambda e: self.plt_canvas_base.configure(scrollregion=self.plt_canvas_base.bbox("all")))
        self.plt_canvas_base.bind("<Configure>", on_canvas_resize)
        #self.plt_canvas_base.configure(yscrollcommand=self.fig_yscroll.set, xscrollcommand=self.fig_xscroll.set)
        
        self.fig_canvas = FigureCanvasTkAgg(self.fig_plane, master=self.fig_frame)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().grid(row=0, column=0, sticky='news')
        
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(1, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(1, weight=1)
        
        # ウィンドウリサイズに対する設定
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
    def create_menubar(self):
        self.master.option_add('*tearOff', False)
        
        self.menubar = tk.Menu(self.master)
        
        self.menu_file = tk.Menu(self.menubar)
        self.menu_option = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)
        
        self.menubar.add_cascade(menu=self.menu_file, label='ファイル')
        self.menubar.add_cascade(menu=self.menu_option, label='オプション')
        self.menubar.add_cascade(menu=self.menu_help, label='ヘルプ')
        
        self.menu_file.add_command(label='開く...', command=self.open_mapfile, accelerator='Control+O')
        self.menu_file.add_command(label='リロード', command=self.reload_map, accelerator='F5')
        self.menu_file.add_separator()
        self.menu_file.add_command(label='図を保存...', command=self.save_plots, accelerator='Control+S')
        self.menu_file.add_command(label='軌道座標を保存...', command=self.save_trackdata)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='終了', command=self.ask_quit, accelerator='Alt+F4')
        
        self.menu_option.add_command(label='座標制御点...', command=self.set_arbcpdist)
        self.menu_option.add_command(label='描画可能区間...', command=self.set_plotlimit)
        self.menu_option.add_command(label='断面図y軸範囲...', command=self.set_profYlimit)
        self.menu_option.add_command(label='Font...', command=self.fontctrl.create_window)
        
        #self.menu_option.add_command(label='customdialog...', command=self.customdialog_test)
        
        self.menu_help.add_command(label='ヘルプ...', command=self.open_webdocument)
        self.menu_help.add_command(label='Kobushiについて...', command=self.aboutwindow)
        
        self.master['menu'] = self.menubar
    def bind_keyevent(self):
        self.bind_all("<Control-o>", self.open_mapfile)
        self.bind_all("<Control-s>", self.save_plots)
        self.bind_all("<F5>", self.reload_map)
        self.bind_all("<Alt-F4>", self.ask_quit)
        self.bind_all("<Return>", self.distset_entry)
        self.bind_all("<Shift-Left>", self.press_arrowkey)
        self.bind_all("<Shift-Right>", self.press_arrowkey)
    def open_mapfile(self, event=None,inputdir=None):
        inputdir = filedialog.askopenfilename() if inputdir is None else inputdir
        if inputdir != '':
            self.filedir_entry_val.set(inputdir)
            
            interpreter = interp.ParseMap(None,self.parser)
            self.result = interpreter.load_files(inputdir)
            
            self.dist_range_sel.set('all')
            if(len(self.result.station.position) > 0):
                self.dmin = round(min(self.result.station.position.keys()),-2) - 500
                self.dmax = round(max(self.result.station.position.keys()),-2) + 500
                self.distrange_min = self.dmin
                self.distrange_max = self.dmax
                self.setdist_entry_val.set(self.dmin)
                self.distance_scale.set(0)
            else:
                self.dmin = round(min(self.result.controlpoints.list_cp),-2) - 500
                self.dmax = round(max(self.result.controlpoints.list_cp),-2) + 500
                self.distrange_min = self.dmin
                self.distrange_max = self.dmax
                self.setdist_entry_val.set(self.dmin)
                self.distance_scale.set(0)
                
            '''
            self.distrange_min/max: 対象のマップで表示可能な距離程の最大最小値を示す
            self.dmin/dmax : 実際に画面にプロットする距離程の範囲を示す
            '''
                
            # 他軌道のラインカラーを設定
            self.result.othertrack_linecolor = {}
            linecolor_default = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
            color_ix = 0
            for key in self.result.othertrack.data.keys():
                self.result.othertrack_linecolor[key] = {'current':linecolor_default[color_ix%10], 'default':linecolor_default[color_ix%10]}
                color_ix += 1
                
            # 駅ジャンプメニュー更新
            stnlist_tmp = []
            self.stationlist_cb['values'] = ()
            for stationkey in self.result.station.stationkey.keys():
                stnlist_tmp.append(stationkey+', '+self.result.station.stationkey[stationkey])
                #self.menu_station.add_command(label=stationkey+', '+self.result.station.stationkey[stationkey], command=lambda: print(stationkey))
            self.stationlist_cb['values'] = tuple(stnlist_tmp)
                
            self.subwindow.set_ottree_value()
            
            self.profYlim = None
            
            self.mplot = mapplot.Mapplot(self.result, unitdist_default=self.default_track_interval)
            self.setdist_all()
            
            self.print_debugdata()
    def reload_map(self, event=None):
        inputdir = self.filedir_entry_val.get()
        if inputdir != '':
            # マップ描画設定の退避
            tmp_cp_arbdistribution   = self.mplot.environment.cp_arbdistribution
            tmp_othertrack_checked   = self.subwindow.othertrack_tree.get_checked()
            tmp_othertrack_linecolor = self.result.othertrack_linecolor
            tmp_othertrack_cprange   = self.result.othertrack.cp_range
            
            interpreter = interp.ParseMap(None,self.parser)
            self.result = interpreter.load_files(inputdir)
            
            
            if(len(self.result.station.position) > 0):
                self.distrange_min = round(min(self.result.station.position.keys()),-2) - 500
                self.distrange_max = round(max(self.result.station.position.keys()),-2) + 500
            else:
                self.distrange_min = round(min(self.result.controlpoints.list_cp),-2) - 500
                self.distrange_max = round(max(self.result.controlpoints.list_cp),-2) + 500

            '''
            self.distrange_min/max: 対象のマップで表示可能な距離程の最大最小値を示す
            self.dmin/dmax : 実際に画面にプロットする距離程の範囲を示す
            '''
                
            # 他軌道のラインカラーを設定
            self.result.othertrack_linecolor = {}
            linecolor_default = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
            color_ix = 0
            for key in self.result.othertrack.data.keys():
                self.result.othertrack_linecolor[key] = {'current':linecolor_default[color_ix%10], 'default':linecolor_default[color_ix%10]}
                color_ix += 1
                
            self.subwindow.set_ottree_value()
            
            # 他軌道の描画情報を復帰
            for key in tmp_othertrack_cprange.keys():
                if key in self.result.othertrack.data.keys():
                    self.result.othertrack.cp_range[key] = tmp_othertrack_cprange[key]
                    self.subwindow.othertrack_tree.set(key,'#1',tmp_othertrack_cprange[key]['min'])
                    self.subwindow.othertrack_tree.set(key,'#2',tmp_othertrack_cprange[key]['max'])
                    self.subwindow.othertrack_tree.tag_configure(key,foreground=tmp_othertrack_linecolor[key]['current'])
                    self.result.othertrack_linecolor[key] = tmp_othertrack_linecolor[key]
                    if key in tmp_othertrack_checked:
                        self.subwindow.othertrack_tree._check_ancestor(key)
                    
                
            # 駅ジャンプメニュー更新
            stnlist_tmp = []
            self.stationlist_cb['values'] = ()
            for stationkey in self.result.station.stationkey.keys():
                stnlist_tmp.append(stationkey+', '+self.result.station.stationkey[stationkey])
                #self.menu_station.add_command(label=stationkey+', '+self.result.station.stationkey[stationkey], command=lambda: print(stationkey))
            self.stationlist_cb['values'] = tuple(stnlist_tmp)
            
            self.mplot = mapplot.Mapplot(self.result,cp_arbdistribution = tmp_cp_arbdistribution)
            self.plot_all()
            
            self.print_debugdata()
    def draw_planerplot(self):
        self.ax_plane.cla()
        ydimlim = {'x0.5':0.5,'x1':1,'x2':2,'x4':4,'x8':8,'x16':16}
        self.mplot.plane(self.ax_plane,\
                         distmin=self.dmin,\
                         distmax=self.dmax,\
                         iswholemap = True if self.dist_range_sel.get()=='all' else False,\
                         othertrack_list = self.subwindow.othertrack_tree.get_checked(),\
                         ydim_expansion = ydimlim[self.ydim_cont_val.get()],\
                         ydim_offset = self.ydim_offset_val.get())
        if self.stationpos_val.get():
            self.mplot.stationpoint_plane(self.ax_plane,labelplot=self.stationlabel_val.get())
        
        self.fig_canvas.draw()
    def draw_profileplot(self):
        self.ax_profile_g.cla()
        self.ax_profile_r.cla()
        self.ax_profile_s.cla()
        
        self.mplot.vertical(self.ax_profile_g,\
                            self.ax_profile_r,\
                            distmin=self.dmin,\
                            distmax=self.dmax,\
                            othertrack_list = self.subwindow.othertrack_tree.get_checked() if self.prof_othert_val.get() else None,\
                            ylim = self.profYlim)
        self.mplot.stationpoint_height(self.ax_profile_g,self.ax_profile_s,labelplot=self.stationlabel_val.get())
        if self.gradientpos_val.get():
            self.mplot.gradient_value(self.ax_profile_g,labelplot=self.gradientval_val.get())
        self.mplot.radius_value(self.ax_profile_r,labelplot=self.curveval_val.get())
        
        self.fig_canvas.draw()
    def print_debugdata(self):
        if not __debug__:
            print('own_track data')
            for i in self.result.own_track.data:
                print(i)
            print('controlpoints list')
            for i in self.result.controlpoints.list_cp:
                print(i)
            print('own_track position')
            for i in self.result.owntrack_pos:
                print(i)
            print('station list')
            for i in self.result.station.position:
                print(i,self.result.station.stationkey[self.result.station.position[i]])
            print('othertrack data')
            for i in self.result.othertrack.data.keys():
                print(i)
                for j in self.result.othertrack.data[i]:
                    print(j)
            print('Track keys:')
            print(self.result.othertrack.data.keys())
            print('othertrack position')
            for i in self.result.othertrack.data.keys():
                print(i)
                for j in self.result.othertrack_pos[i]:
                    print(j)
    def setdist_scale(self, val):
        '''距離程スライドバーの処理
        '''
        if self.result != None:
            pos = float(self.distance_scale.get())
            distmin = ((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*pos/100 + self.distrange_min
            self.setdist_entry_val.set(distmin)
            if(self.dist_range_sel.get() == 'arb'):
                self.dmin = distmin
                self.dmax = distmin + self.dist_range_arb_val.get()
                
                self.plot_all()
    def setdist_all(self):
        if self.result != None:
            self.dmin = self.distrange_min
            self.dmax = self.distrange_max
            
            for key in ['x0.5','x1','x2','x4', 'x8', 'x16']:
                self.ydim_cont[key]['state']='disable'
            self.ydim_offset_entry['state']='disable'
            
            self.plot_all()
    def setdist_arbitrary(self):
        if self.result != None:
            for key in ['x0.5','x1','x2','x4', 'x8', 'x16']:
                self.ydim_cont[key]['state']='normal'
            self.ydim_offset_entry['state']='normal'
            self.setdist_scale(0)
    def distset_entry(self, event=None):
        if self.result != None:
            self.distance_scale.set((self.setdist_entry_val.get()-self.distrange_min)/((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*100)
    def plot_all(self):
        if(self.result != None):
            rcParams['font.family'] = self.fontctrl.get_fontname()
            self.draw_planerplot()
            self.draw_profileplot()
    def ask_quit(self, event=None, ask=True):
        if ask:
            if tk.messagebox.askyesno(message='Kobushi Track Viewerを終了しますか？'):
                self.quit()
        else:
            self.quit()
    def press_arrowkey(self, event=None):
        #print(event.keysym)
        if(event.keysym == 'Left'):
            value = (self.setdist_entry_val.get() -self.dist_range_arb_val.get()/5 -self.distrange_min)/((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*100
            value = 0 if value < 0 else value
            self.distance_scale.set(value)
        elif(event.keysym == 'Right'):
            value = (self.setdist_entry_val.get() + self.dist_range_arb_val.get()/5 - self.distrange_min)/((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*100
            value = 100 if value > 100 else value
            self.distance_scale.set(value)
    def jumptostation(self, event=None):
        value = self.stationlist_cb.get()
        key = value.split(',')[0]
        dist = [k for k, v in self.result.station.position.items() if v == key]
        if len(dist)>0:
            #print(value, dist[0])
            self.setdist_entry_val.set(dist[0]-self.dist_range_arb_val.get()/2)
            self.distset_entry()
        else:
            tk.messagebox.showinfo(message=value+' はこのmap上に見つかりませんでした')
    def save_plots(self, event=None):
        filepath = filedialog.asksaveasfilename(filetypes=[('portable network graphics (png)','*.png'), ('scalable vector graphics (svg)','*.svg'), ('any format','*')], defaultextension='*.*')
        if filepath != '':
            filepath = pathlib.Path(filepath)
            self.fig_plane.savefig(filepath.parent.joinpath(str(filepath.stem) + '' + str(filepath.suffix)))
    def save_trackdata(self, event=None):
        filepath = filedialog.askdirectory(initialdir='./')
        if filepath != '':
            filepath = pathlib.Path(filepath)
            filename_base = filepath.stem
            
            output_filename = filepath.joinpath(str(filename_base)+'_owntrack'+'.csv')
            output = self.result.owntrack_pos
            header = 'distance,x,y,z,direction,radius,gradient,interpolate_func,cant,center,gauge'
            np.savetxt(output_filename, output, delimiter=',',header=header,fmt='%.6f')
            
            for key in self.result.othertrack_pos.keys():
                output_filename = filepath.joinpath(str(filename_base)+'_'+key+'.csv')
                output = self.result.othertrack_pos[key]
                header = 'distance,x,y,z,interpolate_func,cant,center,gauge'
                np.savetxt(output_filename, output, delimiter=',',header=header,fmt='%.6f')
    def set_plotlimit(self, event=None):
        if self.result != None:
            dialog = dialog_multifields.dialog_multifields(self,\
                                            [{'name':'min', 'type':'Double', 'label':'min (default:'+str(self.result.cp_defaultrange[0])+')', 'default':self.distrange_min},\
                                            {'name':'max', 'type':'Double', 'label':'max (default:'+str(self.result.cp_defaultrange[1])+')', 'default':self.distrange_max}],
                                            message ='Set plotlimit\n'+'map range:'+str(min(self.result.controlpoints.list_cp))+','+str(max(self.result.controlpoints.list_cp)))
            if dialog.result == 'OK':
                self.distrange_min = float(dialog.variables['min'].get())
                self.distrange_max = float(dialog.variables['max'].get())
                self.setdist_all()
            elif dialog.result == 'reset':
                self.distrange_min = self.result.cp_defaultrange[0]
                self.distrange_max = self.result.cp_defaultrange[1]
                self.setdist_all()
    def set_arbcpdist(self, event = None):
        if self.result != None:
            cp_arbdistribution = self.mplot.environment.cp_arbdistribution
            cp_arb_default = self.mplot.environment.cp_arbdistribution_default
            list_cp = self.result.controlpoints.list_cp
            boundary_margin = 500
            equaldist_unit = 25
            cp_arbcp_default = [round(min(list_cp),-2) - boundary_margin,round(max(list_cp),-2) + boundary_margin,equaldist_unit]
            
            dialog = dialog_multifields.dialog_multifields(self,\
                                            [{'name':'min', 'type':'Double', 'label':'min (default: '+str(cp_arb_default[0])+')', 'default':cp_arbdistribution[0]},\
                                            {'name':'max', 'type':'Double', 'label':'max (default: '+str(cp_arb_default[1])+')', 'default':cp_arbdistribution[1]},\
                                            {'name':'interval', 'type':'Double', 'label':'interval (default: '+str(cp_arb_default[2])+')', 'default':cp_arbdistribution[2]}],
                                            message ='Set additional controlpoint')
            if dialog.result == 'OK':
                inputval = [dialog.variables['min'].get(),dialog.variables['max'].get(),dialog.variables['interval'].get()]
                for ix in [0,1,2]:
                    self.mplot.environment.cp_arbdistribution[ix] = float(inputval[ix])
                self.reload_map()
            elif dialog.result == 'reset':
                for ix in [0,1,2]:
                    self.mplot.environment.cp_arbdistribution = None
                self.reload_map()
    def set_profYlimit(self, event=None):
        if self.result != None:
            dialog = dialog_multifields.dialog_multifields(self,\
                                            [{'name':'min', 'type':'str', 'label':'min (default:auto)', 'default':'auto' if self.profYlim == None else str(self.profYlim[0])},\
                                            {'name':'max', 'type':'str', 'label':'max (default:auto)', 'default':'auto' if self.profYlim == None else str(self.profYlim[1])}],
                                            message ='Set profile Y limit')
            if dialog.result == 'reset':
                self.profYlim = None
                self.plot_all()
            elif dialog.result == 'OK':
                if dialog.variables['min'].get() != 'auto' and dialog.variables['max'].get() != 'auto':
                    self.profYlim = [float(dialog.variables['min'].get()),float(dialog.variables['max'].get())]
                else:
                    self.profYlim = None
                self.plot_all()
    def aboutwindow(self, event=None):
        msg  = 'Kobushi trackviewer\n'
        msg += 'Version '+__version__+'\n\n'
        msg += 'Copyright © 2021-2024 konawasabi\n'
        msg += 'Released under the Apache License, Version 2.0 .\n'
        msg += 'https://www.apache.org/licenses/LICENSE-2.0'
        tk.messagebox.showinfo(message=msg)
    def customdialog_test(self, event=None):
        dialog_obj = dialog_multifields.dialog_multifields(self,\
                                        [{'name':'A', 'type':'str', 'label':'test A', 'default':'alpha'},\
                                        {'name':'B', 'type':'Double', 'label':'test B', 'default':100}],\
                                        'Test Dialog')
        print('Done', dialog_obj.result, dialog_obj.variables['A'].get())
    def open_webdocument(self, event=None):
        webbrowser.open('https://github.com/konawasabi/kobushi-trackviewer/blob/master/reference.md')
#if __name__ == '__main__':
def main():
    if not __debug__:
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
        #import sys
        sys.excepthook = info
        print('Debug mode')

    argparser = argparse.ArgumentParser()
    argparser.add_argument('filepath', metavar='F', type=str, help='input mapfile', nargs='?')
    argparser.add_argument('-s', '--step', help='distance interval for track calculation', type=float, default=25)
    argparser.add_argument('-f', '--font', help='Font', type=str, default = 'sans-serif')
    args = argparser.parse_args()
       
    tk.CallWrapper = Catcher
    root = tk.Tk()
    app = mainwindow(master=root, parser = None, stepdist = args.step, font=args.font)

    if args.filepath is not None:
        app.open_mapfile(inputdir=args.filepath)
    app.mainloop()
