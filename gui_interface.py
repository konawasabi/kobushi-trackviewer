import sys

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams

import lark
from lark import Lark, Transformer, v_args, exceptions

# https://qiita.com/yniji/items/3fac25c2ffa316990d0c matplotlibで日本語を使う
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

import mapinterpleter as interp
import mapplot

class mainwindow(ttk.Frame):
    def __init__(self, master, parser):
        self.dmin = None
        self.dmax = None
        
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Kobushi Track Viewer')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()
        self.parser = parser
        
        
    def create_widgets(self):
        self.control_frame = ttk.Frame(self, padding='3 3 3 3')
        self.control_frame.grid(column=1, row=1, sticky=(tk.S))
        
        self.saveplots_btn = ttk.Button(self.control_frame, text="Save plots", command=None)
        self.saveplots_btn.grid(column=0, row=0, sticky=(tk.W, tk.E))
        self.savetrack_btn = ttk.Button(self.control_frame, text="Save track", command=None)
        self.savetrack_btn.grid(column=0, row=1, sticky=(tk.W, tk.E))
        self.quit_btn = ttk.Button(self.control_frame, text="Quit", command=self.quit)
        self.quit_btn.grid(column=0, row=10, sticky=(tk.W, tk.E))
        
        self.file_frame = ttk.Frame(self, padding='3 3 3 3')
        self.file_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.open_btn = ttk.Button(self.file_frame, text="Open", command=self.open_mapfile)
        self.open_btn.grid(column=0, row=0, sticky=(tk.W))
        
        self.filedir_entry_val = tk.StringVar()
        self.filedir_entry = ttk.Entry(self.file_frame, width=75, textvariable=self.filedir_entry_val)
        self.filedir_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.setdist_frame = ttk.Frame(self, padding='3 3 3 3')
        self.setdist_frame.grid(column=0, row=2, sticky=(tk.W, tk.E))
        
        self.setdist_entry_val = tk.DoubleVar()
        self.setdist_entry = ttk.Entry(self.setdist_frame, width=7, textvariable=self.setdist_entry_val)
        self.setdist_entry.grid(column=0, row=0, sticky=(tk.W, tk.E))
        
        self.distance_scale = ttk.Scale(self.setdist_frame, orient=tk.HORIZONTAL, length=500, from_=0, to=100, command=self.setdist_scale)
        self.distance_scale.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.dist_range_sel = tk.StringVar(value='all')
        #self.dist_range = ttk.Combobox(self.setdist_frame, textvariable=self.dist_range_val, width = 6, state='readonly')
        #self.dist_range['values'] = ('all', '10 km', '5 km', '2 km', '1 km', '500 m', '200 m', '100 m')
        self.dist_range_all = ttk.Radiobutton(self.setdist_frame, text='all',variable=self.dist_range_sel, value='all', command=self.setdist_all)
        self.dist_range_all.grid(column=2, row=0, sticky=(tk.W, tk.E))
        self.dist_range_arb = ttk.Radiobutton(self.setdist_frame, text='',variable=self.dist_range_sel, value='arb', command=self.setdist_arbitrary)
        self.dist_range_arb.grid(column=3, row=0, sticky=(tk.W, tk.E))
        self.dist_range_arb_val = tk.DoubleVar(value=5000)
        self.dist_range_arb_entry = ttk.Entry(self.setdist_frame, width=5, textvariable=self.dist_range_arb_val)
        self.dist_range_arb_entry.grid(column=4, row=0, sticky=(tk.W, tk.E))
        
        self.canvas_frame = ttk.Frame(self, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_plane = plt.figure(figsize=(8,5))
        self.ax_plane = self.fig_plane.add_subplot()
        
        self.plane_canvas = FigureCanvasTkAgg(self.fig_plane, master=self.canvas_frame)
        self.plane_canvas.draw()
        self.plane_canvas.get_tk_widget().grid(row = 0, column = 0)
        
        self.fig_profile = plt.figure(figsize=(8,3))
        self.ax_profile_g = self.fig_profile.add_subplot(2,1,1)
        self.ax_profile_r = self.fig_profile.add_subplot(2,1,2)
        
        self.profile_canvas = FigureCanvasTkAgg(self.fig_profile, master=self.canvas_frame)
        self.profile_canvas.draw()
        self.profile_canvas.get_tk_widget().grid(row = 1, column = 0)
    
    def open_mapfile(self):
        inputdir = filedialog.askopenfilename()
        if inputdir != '':
            self.filedir_entry_val.set(inputdir)
            
            interpreter = interp.ParseMap(None,self.parser)
            self.result = interpreter.load_files(inputdir)
            
            self.dist_range_sel.set('all')
            if(len(self.result.station.position) > 0):
                self.dmin = min(self.result.station.position.keys()) - 500
                self.dmax = max(self.result.station.position.keys()) + 500
                self.distrange_min = self.dmin
                self.distrange_max = self.dmax
                self.setdist_entry_val.set(self.dmin)
                self.distance_scale.set(0)
                
            self.mplot = mapplot.Mapplot(self.result)
            self.draw_planerplot()
            self.draw_profileplot()
            
            self.print_debugdata()
    def draw_planerplot(self):
        self.ax_plane.cla()
        
        self.mplot.plane(self.ax_plane,distmin=self.dmin,distmax=self.dmax)
        self.mplot.stationpoint_plane(self.ax_plane)
        
        self.plane_canvas.draw()
    def draw_profileplot(self):
        self.ax_profile_g.cla()
        self.ax_profile_r.cla()
        
        self.mplot.vertical(self.ax_profile_g, self.ax_profile_r,distmin=self.dmin,distmax=self.dmax)
        self.mplot.stationpoint_height(self.ax_profile_g)
        self.mplot.gradient_value(self.ax_profile_g)
        self.mplot.radius_value(self.ax_profile_r)
        
        self.profile_canvas.draw()
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
    def setdist_scale(self, val):
        if(self.dist_range_sel.get() == 'arb'):
            pos = float(self.distance_scale.get())
            distmin = ((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*pos/100 + self.distrange_min
            self.setdist_entry_val.set(distmin)
            
            self.dmin = distmin
            self.dmax = distmin + self.dist_range_arb_val.get()
            
            self.draw_planerplot()
            self.draw_profileplot()
    def setdist_all(self):
        self.dmin = self.distrange_min
        self.dmax = self.distrange_max
        
        self.draw_planerplot()
        self.draw_profileplot()
    def setdist_arbitrary(self):
        self.setdist_scale(0)

if __name__ == '__main__':
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
        import sys
        sys.excepthook = info
    
    rule = open('map-grammer.lark', encoding='utf-8').read()
    
    root = tk.Tk()
    app = mainwindow(master=root, parser = Lark(rule, parser='lalr', maybe_placeholders=True))
    app.mainloop()