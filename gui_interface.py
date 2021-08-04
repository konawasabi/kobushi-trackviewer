import sys

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
from ttkwidgets import CheckboxTreeview

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

# http://centerwave-callout.com/tkinter内で起きた例外をどうキャッチするか？/
class Catcher:
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
            raise e

class mainwindow(ttk.Frame):
    class SubWindow(ttk.Frame):
        def __init__(self, master, mainwindow):
            self.mainwindow = mainwindow
            self.parent = master
            super().__init__(master, padding='3 3 3 3')
            
            self.mainwindow.tk.eval("""
                ttk::style map Treeview \
                -foreground {disabled SystemGrayText \
                             selected SystemHighlightText} \
                -background {disabled SystemButtonFace \
                             selected SystemHighlight}
            """)
            
            self.master.title('Other tracks')
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.create_widgets()
            self.master.geometry('+1100+0')
        def create_widgets(self):
            self.othertrack_tree = CheckboxTreeview(self, show='tree headings', columns=['mindist', 'maxdist', 'linecolor'],selectmode='browse')
            self.othertrack_tree.bind("<ButtonRelease>", self.click_tracklist)
            self.othertrack_tree.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
            self.othertrack_tree.column('#0', width=200)
            self.othertrack_tree.column('mindist', width=100)
            self.othertrack_tree.column('maxdist', width=100)
            self.othertrack_tree.column('linecolor', width=50)
            self.othertrack_tree.heading('#0', text='track key')
            self.othertrack_tree.heading('mindist', text='From')
            self.othertrack_tree.heading('maxdist', text='To')
            self.othertrack_tree.heading('linecolor', text='Color')
            
            self.ottree_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.othertrack_tree.yview)
            self.ottree_scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
            self.othertrack_tree.configure(yscrollcommand=self.ottree_scrollbar.set)
            
            '''
            def fixed_map(option):
                return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]
            style = ttk.Style()
            style.configure("Treeview.Heading", font=("YU Mincho", 12, "bold", "italic", "underline" ), rowheight=100, foreground="black")
            style.configure("Treeview", font=("Arial", 10, "overstrike"), rowheight=50)
            style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
            '''
            
            #self.otselect_btn = ttk.Button(self, text="Checked track", command=self.print_checkedtrack())
            #self.otselect_btn.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E))
        def click_tracklist(self, event=None):
            '''他軌道リストをクリックしたときのイベント処理
            '''
            columnlabel = {'#0':'Check','#1':'From', '#2':'To', '#3':'Color'}
            if event != None:
                if getattr(event, 'widget').identify("element", event.x, event.y) == 'text': #数値部分クリックかどうか。チェックボックスだとimage
                    cliked_column = self.othertrack_tree.identify_column(event.x)
                    cliked_track = self.othertrack_tree.identify_row(event.y)
                    #print(cliked_track,columnlabel[cliked_column])
                    if cliked_column in ['#1','#2'] and cliked_track != 'root':
                        if cliked_column == '#1':
                            defaultval = min(self.mainwindow.result.othertrack.data[cliked_track], key=lambda x: x['distance'])['distance']
                        elif cliked_column == '#2':
                            defaultval = max(self.mainwindow.result.othertrack.data[cliked_track], key=lambda x: x['distance'])['distance']
                        inputdata = simpledialog.askfloat(cliked_track+': Distance', columnlabel[cliked_column]+' (default: '+str(defaultval)+' m)')
                        #print(inputdata)
                        if inputdata != None: # 入力値に問題なければ、描画範囲を変更する
                            if cliked_column == '#1':
                                self.mainwindow.result.othertrack.cp_range[cliked_track]['min'] = inputdata
                            elif cliked_column == '#2':
                                self.mainwindow.result.othertrack.cp_range[cliked_track]['max'] = inputdata
                            self.othertrack_tree.set(cliked_track,cliked_column,inputdata) # 他軌道リストの表示値変更
            self.mainwindow.plot_all()
        def set_ottree_value(self):
            if self.othertrack_tree.exists('root'):
                self.othertrack_tree.delete('root')
            self.othertrack_tree.insert("", "end", 'root', text='root', open=True)
            colorix = 0
            for i in self.mainwindow.result.othertrack.data.keys():
                self.othertrack_tree.insert("root", "end", i, text=i, values=(min(self.mainwindow.result.othertrack.data[i], key=lambda x: x['distance'])['distance'],max(self.mainwindow.result.othertrack.data[i], key=lambda x: x['distance'])['distance'], '■■■'),tags=(i,))
                self.othertrack_tree.tag_configure(i,foreground=self.mainwindow.result.othertrack_linecolor[i])
            #self.subwindow.othertrack_tree.see('root')
            #self.othertrack_tree.configure(yscrollcommand=self.ottree_scrollbar.set)
            
    def __init__(self, master, parser):
        self.dmin = None
        self.dmax = None
        self.result = None
        
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Kobushi Track Viewer')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        master.protocol('WM_DELETE_WINDOW', self.ask_quit)
        
        self.create_widgets()
        self.create_menubar()
        self.bind_keyevent()
        self.subwindow = self.SubWindow(tk.Toplevel(master), self)
        
        self.parser = parser

    def create_widgets(self):
        self.control_frame = ttk.Frame(self, padding='3 3 3 3')
        self.control_frame.grid(column=1, row=1, sticky=(tk.S))
        
        self.stationpos_val = tk.BooleanVar(value=True)
        self.stationpos_chk = ttk.Checkbutton(self.control_frame, text='駅座標',onvalue=True, offvalue=False, variable=self.stationpos_val, command=self.plot_all)
        self.stationpos_chk.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        self.stationlabel_val = tk.BooleanVar(value=True)
        self.stationlabel_chk = ttk.Checkbutton(self.control_frame, text='駅名',onvalue=True, offvalue=False, variable=self.stationlabel_val, command=self.plot_all)
        self.stationlabel_chk.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E))
        self.gradientpos_val = tk.BooleanVar(value=True)
        self.gradientpos_chk = ttk.Checkbutton(self.control_frame, text='勾配変化点',onvalue=True, offvalue=False, variable=self.gradientpos_val, command=self.plot_all)
        self.gradientpos_chk.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E))
        self.gradientval_val = tk.BooleanVar(value=True)
        self.gradientval_chk = ttk.Checkbutton(self.control_frame, text='勾配値',onvalue=True, offvalue=False, variable=self.gradientval_val, command=self.plot_all)
        self.gradientval_chk.grid(column=0, row=3, sticky=(tk.N, tk.W, tk.E))
        self.curveval_val = tk.BooleanVar(value=True)
        self.curveval_chk = ttk.Checkbutton(self.control_frame, text='曲線半径',onvalue=True, offvalue=False, variable=self.curveval_val, command=self.plot_all)
        self.curveval_chk.grid(column=0, row=4, sticky=(tk.N, tk.W, tk.E))
        
        self.file_frame = ttk.Frame(self, padding='3 3 3 3')
        self.file_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.open_btn = ttk.Button(self.file_frame, text="Open", command=self.open_mapfile)
        self.open_btn.grid(column=0, row=0, sticky=(tk.W))
        
        self.filedir_entry_val = tk.StringVar()
        self.filedir_entry = ttk.Entry(self.file_frame, width=75, textvariable=self.filedir_entry_val)
        self.filedir_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.setdist_frame = ttk.Frame(self, padding='3 3 3 3')
        self.setdist_frame.grid(column=0, row=2, sticky=(tk.W, tk.E))
        
        self.distset_btn = ttk.Button(self.setdist_frame, text="Set", command=self.distset_entry, width=3)
        self.distset_btn.grid(column=0, row=0, sticky=(tk.W, tk.E))
        
        self.setdist_entry_val = tk.DoubleVar()
        self.setdist_entry = ttk.Entry(self.setdist_frame, width=7, textvariable=self.setdist_entry_val)
        self.setdist_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        
        self.distance_scale = ttk.Scale(self.setdist_frame, orient=tk.HORIZONTAL, length=500, from_=0, to=100, command=self.setdist_scale)
        self.distance_scale.grid(column=2, row=0, sticky=(tk.W, tk.E))
        
        self.dist_range_sel = tk.StringVar(value='all')
        #self.dist_range = ttk.Combobox(self.setdist_frame, textvariable=self.dist_range_val, width = 6, state='readonly')
        #self.dist_range['values'] = ('all', '10 km', '5 km', '2 km', '1 km', '500 m', '200 m', '100 m')
        self.dist_range_all = ttk.Radiobutton(self.setdist_frame, text='all',variable=self.dist_range_sel, value='all', command=self.setdist_all)
        self.dist_range_all.grid(column=3, row=0, sticky=(tk.W, tk.E))
        self.dist_range_arb = ttk.Radiobutton(self.setdist_frame, text='',variable=self.dist_range_sel, value='arb', command=self.setdist_arbitrary)
        self.dist_range_arb.grid(column=4, row=0, sticky=(tk.W, tk.E))
        self.dist_range_arb_val = tk.DoubleVar(value=5000)
        self.dist_range_arb_entry = ttk.Entry(self.setdist_frame, width=5, textvariable=self.dist_range_arb_val)
        self.dist_range_arb_entry.grid(column=5, row=0, sticky=(tk.W, tk.E))
        
        
        self.canvas_frame = ttk.Frame(self, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_plane = plt.figure(figsize=(10,5))
        self.ax_plane = self.fig_plane.add_subplot()
        
        self.plane_canvas = FigureCanvasTkAgg(self.fig_plane, master=self.canvas_frame)
        self.plane_canvas.draw()
        self.plane_canvas.get_tk_widget().grid(row = 0, column = 0)
        
        self.fig_profile, ((self.ax_profile_s, self.ax_profile_g, self.ax_profile_r)) = plt.subplots(3,1, figsize=(10,3), sharex='col', gridspec_kw={'height_ratios': [3, 6, 4]})
        self.fig_profile.subplots_adjust(hspace=0)
        self.ax_profile_s.tick_params(labelleft=False, left=False)
        self.ax_profile_r.tick_params(labelleft=False, left=False)
        
        self.profile_canvas = FigureCanvasTkAgg(self.fig_profile, master=self.canvas_frame)
        self.profile_canvas.draw()
        self.profile_canvas.get_tk_widget().grid(row = 1, column = 0)
    def create_menubar(self):
        self.master.option_add('*tearOff', False)
        
        menubar = tk.Menu(self.master)
        
        menu_file = tk.Menu(menubar)
        menu_option = tk.Menu(menubar)
        
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_option, label='Option')
        
        menu_file.add_command(label='Open...', command=self.open_mapfile, accelerator='Control+O')
        menu_file.add_separator()
        menu_file.add_command(label='Save plots...', command=None, accelerator='Control+S')
        menu_file.add_command(label='Save track data...', command=None)
        menu_file.add_separator()
        menu_file.add_command(label='Quit', command=self.ask_quit, accelerator='Alt+F4')
        
        self.master['menu'] = menubar
    def bind_keyevent(self):
        self.bind_all("<Control-o>", self.open_mapfile)
        self.bind_all("<Alt-F4>", self.ask_quit)
        self.bind_all("<Return>", self.distset_entry)
        self.bind_all("<Shift-Left>", self.press_arrowkey)
        self.bind_all("<Shift-Right>", self.press_arrowkey)
    def open_mapfile(self, event=None):
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
            else:
                self.dmin = min(self.result.controlpoints.list_cp)
                self.dmax = max(self.result.controlpoints.list_cp)
                self.distrange_min = self.dmin
                self.distrange_max = self.dmax
                self.setdist_entry_val.set(self.dmin)
                self.distance_scale.set(0)
                
            self.subwindow.set_ottree_value()
            
            self.mplot = mapplot.Mapplot(self.result)
            self.plot_all()
            
            self.print_debugdata()
    def draw_planerplot(self):
        self.ax_plane.cla()
        
        self.mplot.plane(self.ax_plane,distmin=self.dmin,distmax=self.dmax,iswholemap = True if self.dist_range_sel.get()=='all' else False, othertrack_list = self.subwindow.othertrack_tree.get_checked())
        if self.stationpos_val.get():
            self.mplot.stationpoint_plane(self.ax_plane,labelplot=self.stationlabel_val.get())
        
        self.plane_canvas.draw()
    def draw_profileplot(self):
        self.ax_profile_g.cla()
        self.ax_profile_r.cla()
        self.ax_profile_s.cla()
        
        self.mplot.vertical(self.ax_profile_g, self.ax_profile_r,distmin=self.dmin,distmax=self.dmax)
        self.mplot.stationpoint_height(self.ax_profile_g,self.ax_profile_s,labelplot=self.stationlabel_val.get())
        if self.gradientpos_val.get():
            self.mplot.gradient_value(self.ax_profile_g,labelplot=self.gradientval_val.get())
        self.mplot.radius_value(self.ax_profile_r,labelplot=self.curveval_val.get())
        
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
        pos = float(self.distance_scale.get())
        distmin = ((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*pos/100 + self.distrange_min
        self.setdist_entry_val.set(distmin)
        if(self.dist_range_sel.get() == 'arb'):
            self.dmin = distmin
            self.dmax = distmin + self.dist_range_arb_val.get()
            
            self.plot_all()
    def setdist_all(self):
        self.dmin = self.distrange_min
        self.dmax = self.distrange_max
        
        self.plot_all()
    def setdist_arbitrary(self):
        self.setdist_scale(0)
    def distset_entry(self, event=None):
        self.distance_scale.set((self.setdist_entry_val.get()-self.distrange_min)/((self.distrange_max-self.dist_range_arb_val.get()) - self.distrange_min)*100)
    def plot_all(self):
        if(self.result != None):
            self.draw_planerplot()
            self.draw_profileplot()
    def ask_quit(self, event=None):
        if tk.messagebox.askyesno(message='Kobushi Track Viewerを終了しますか？'):
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
    
    tk.CallWrapper = Catcher
    root = tk.Tk()
    app = mainwindow(master=root, parser = Lark(rule, parser='lalr', maybe_placeholders=True))
    app.mainloop()
