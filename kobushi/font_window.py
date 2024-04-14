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

import tkinter as tk
from tkinter import ttk
from matplotlib.font_manager import FontManager

class FontControl():
    def __init__(self, master, mainwindow):
        self.mainwindow = mainwindow
        self.master= None
        self.parent = master

        fm = FontManager()
        self.mat_fonts = set(f.name for f in fm.ttflist)
        self.mat_fonts.add('sans-serif')
        self.fontname = 'sans-serif'

        
    def create_window(self,event=None):
        if self.master is None:
            self.master = tk.Toplevel(self.mainwindow)
            self.master.title('Font')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)
            self.master.focus_set()
        
            self.frame = ttk.Frame(self.master, padding=5)
            self.frame.grid(sticky=(tk.N, tk.W, tk.E, tk.S))
            self.frame.columnconfigure(0,weight=1)
            self.frame.rowconfigure(0,weight=1)
            self.combobox = ttk.Combobox(self.frame, width=30,values=sorted(self.mat_fonts))
            self.combobox.grid(column=0,row=0)
            self.combobox.set(self.fontname)


            self.subframe = ttk.Frame(self.frame, padding=5)
            self.subframe.grid(column=0,row=1,sticky=(tk.N, tk.W, tk.E, tk.S))
            self.ok_button = ttk.Button(self.subframe, text='OK', command=self.ok_close)
            self.ok_button.grid(column=0,row=0)
            self.cancel_button = ttk.Button(self.subframe, text='Cancel', command=self.closewindow)
            self.cancel_button.grid(column=1,row=0)
    def closewindow(self):
        self.master.withdraw()
        self.master = None
    def ok_close(self):
        self.fontname = self.combobox.get()
        self.closewindow()
        self.mainwindow.plot_all()
    def set_fontname(self, font):
        self.fontname = font
    def get_fontname(self):
        return self.fontname
        
        
        
