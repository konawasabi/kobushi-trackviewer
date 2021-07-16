import sys

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams

import lark
from lark import Lark, Transformer, v_args, exceptions

import numpy as np

# https://qiita.com/yniji/items/3fac25c2ffa316990d0c matplotlibで日本語を使う
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

import mapinterpleter as interp
import mapplot

class mainwindow(ttk.Frame):
    def __init__(self, master, interpreter):
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Kobushi Track Viewer')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()
        self.interpreter = interpreter
        
        self.X = np.linspace(-np.pi,np.pi,100)
        
    def create_widgets(self):
        self.control_frame = ttk.Frame(self, padding='3 3 3 3')
        self.control_frame.grid(column=1, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.sin_btn = ttk.Button(self.control_frame, text="Sin", command=self.plotsin)
        self.sin_btn.grid(column=0, row=1, sticky=(tk.N, tk.S))
        self.cos_btn = ttk.Button(self.control_frame, text="Cos", command=self.plotcos)
        self.cos_btn.grid(column=0, row=2, sticky=(tk.N, tk.S))
        
        self.file_frame = ttk.Frame(self, padding='3 3 3 3')
        self.file_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.open_btn = ttk.Button(self.file_frame, text="Open", command=self.open_mapfile)
        self.open_btn.grid(column=0, row=0, sticky=(tk.N, tk.S))
        
        self.filedir_entry_val = tk.StringVar()
        self.filedir_entry = ttk.Entry(self.file_frame, width=75, textvariable=self.filedir_entry_val)
        self.filedir_entry.grid(column=1, row=0, sticky=(tk.N, tk.S))
        
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
        self.filedir_entry_val.set(inputdir)
        
        self.result = self.interpreter.load_files(inputdir)
        
        if(len(self.result.station.position) > 0):
            dmin = min(self.result.station.position.keys()) - 500
            dmax = max(self.result.station.position.keys()) + 500
        else:
            dmin = None
            dmax = None
            
        mplot = mapplot.Mapplot(self.result)
        self.ax_plane.cla()
        self.ax_profile_g.cla()
        self.ax_profile_r.cla()
        
        mplot.plane(self.ax_plane,distmin=dmin,distmax=dmax)
        mplot.vertical(self.ax_profile_g, self.ax_profile_r,distmin=dmin,distmax=dmax)
        mplot.stationpoint_plane(self.ax_plane)
        mplot.stationpoint_height(self.ax_profile_g)
        mplot.gradient_value(self.ax_profile_g)
        mplot.radius_value(self.ax_profile_r)
        
        self.plane_canvas.draw()
        self.profile_canvas.draw()
    
    def plotsin(self):
        self.ax_plane.cla()
        self.ax_plane.plot(self.X,np.sin(self.X))
        self.plane_canvas.draw()
    def plotcos(self):
        self.ax_plane.cla()
        self.ax_plane.plot(self.X,np.cos(self.X))
        self.plane_canvas.draw()

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
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    
    root = tk.Tk()
    app = mainwindow(master=root,interpreter = interp.ParseMap(None,parser))
    app.mainloop()
