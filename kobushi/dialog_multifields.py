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

import tkinter as tk
from tkinter import ttk

class dialog_multifields(ttk.Frame):
    def __init__(self, mainwindow, variable, title=None, message=None):
        self.mainwindow = mainwindow
        self.master = tk.Toplevel(self.mainwindow)
        super().__init__(self.master, padding='3 3 3 3')
        if title != None:
            self.master.title(title)
        else:
            self.master.title('')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets(variable, message)
        self.master.bind("<Return>", self.clickOk)
        self.master.bind("<Escape>", self.clickCancel)
        
        self.result = False
        
        self.master.focus_set()
        self.master.grab_set()
        self.master.transient(self.mainwindow)
        self.master.wait_window()
    def create_widgets(self,variable,message):
        self.variables = {}
        self.entries = {}
        self.labels = {}
        
        if message != None:
            self.message_label = ttk.Label(self,text = message)
            self.message_label.grid(column=0, row=0, sticky=(tk.W,tk.N))
        
        self.entry_frame = ttk.Frame(self, padding='3 3 3 3')
        self.entry_frame.grid(column=0, row=1, sticky=(tk.N))
        
        ix=0
        for key in variable:
            if key['type'] == 'str':
                self.variables[key['name']] = tk.StringVar()
            else:
                self.variables[key['name']] = tk.DoubleVar()
            self.labels[key['name']] = ttk.Label(self.entry_frame,text = key['label'])
            self.labels[key['name']].grid(column=0, row=ix, sticky=(tk.W))
            self.entries[key['name']] = ttk.Entry(self.entry_frame,textvariable=self.variables[key['name']],width=7)
            self.entries[key['name']].grid(column=1, row=ix, sticky=(tk.E))
            self.variables[key['name']].set(key['default'])
            ix+=1
        
        self.button_frame = ttk.Frame(self, padding='3 3 3 3')
        self.button_frame.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.button_ok = ttk.Button(self.button_frame, text="OK", command=self.clickOk)
        self.button_ok.grid(column=0, row=0, sticky=(tk.S))
        self.button_reset = ttk.Button(self.button_frame, text="Reset", command=self.clickreset)
        self.button_reset.grid(column=1, row=0, sticky=(tk.S))
        self.button_cancel = ttk.Button(self.button_frame, text="Cancel", command=self.clickCancel)
        self.button_cancel.grid(column=2, row=0, sticky=(tk.S))
    def clickOk(self, event=None):
        self.result = 'OK'
        self.master.destroy()
    def clickreset(self, event=None):
        self.result = 'reset'
        self.master.destroy()
    def clickCancel(self, event=None):
        self.master.destroy()
