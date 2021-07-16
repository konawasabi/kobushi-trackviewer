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
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Kobushi Track Viewer')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()
        self.parser = parser
        
    def create_widgets(self):
        self.control_frame = ttk.Frame(self, padding='3 3 3 3')
        self.control_frame.grid(column=1, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.save_btn = ttk.Button(self.control_frame, text="Save", command=None)
        self.save_btn.grid(column=0, row=0, sticky=(tk.N, tk.S))
        self.save_btn = ttk.Button(self.control_frame, text="Quit", command=self.quit)
        self.save_btn.grid(column=0, row=10, sticky=(tk.N, tk.S))
        
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
        if inputdir != '':
            self.filedir_entry_val.set(inputdir)
            
            interpreter = interp.ParseMap(None,self.parser)
            self.result = interpreter.load_files(inputdir)
            
            if(len(self.result.station.position) > 0):
                self.dmin = min(self.result.station.position.keys()) - 500
                self.dmax = max(self.result.station.position.keys()) + 500
            else:
                self.dmin = None
                self.dmax = None
                
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
