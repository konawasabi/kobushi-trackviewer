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
import lark
from lark import Lark, Transformer, v_args, exceptions
import sys
import matplotlib.pyplot as plt
from matplotlib import rcParams

# https://qiita.com/yniji/items/3fac25c2ffa316990d0c matplotlibで日本語を使う
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

from . import mapinterpleter as interp
from . import mapplot

if __name__ == '__main__':
    rule = open('map-grammer.lark', encoding='utf-8').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    interpreter = interp.ParseMap(None,parser)
    
    argvs = sys.argv
    
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
    
    try:
        result = interpreter.load_files(argvs[1])
    except exceptions.VisitError as e:
        print(e.orig_exc)
        #print(vars(e))
        #print(e)
        if not __debug__:
            raise
        else:
            sys.exit()
    except Exception as e:
        print('Unexpected error.')
        #print(type(e))
        print(e)
        if not __debug__:
            raise
        else:
            sys.exit()
    
    if not __debug__:
        print('own_track data')
        for i in result.own_track.data:
            print(i)
            
        print('controlpoints list')
        for i in result.controlpoints.list_cp:
            print(i)
            
    
    print('station list')
    for i in result.station.position:
        print(i,result.station.stationkey[result.station.position[i]])
        
    if(len(result.station.position) > 0):
        dmin = min(result.station.position.keys()) - 500
        dmax = max(result.station.position.keys()) + 500
    else:
        dmin = None
        dmax = None
        
    mplot = mapplot.Mapplot(result)
    
    planer_fig = plt.figure()
    ax1 = planer_fig.add_subplot(1,1,1)
    
    profile_fig = plt.figure()
    ax2 = profile_fig.add_subplot(3,1,1)
    ax3 = profile_fig.add_subplot(3,1,2)
    ax4 = profile_fig.add_subplot(3,1,3)
    
    mplot.plane(ax1,distmin=dmin,distmax=dmax,iswholemap = True)
    mplot.vertical(ax2, ax3,distmin=dmin,distmax=dmax)
    mplot.stationpoint_plane(ax1)
    mplot.stationpoint_height(ax2,ax4)
    mplot.gradient_value(ax2)
    mplot.radius_value(ax3)
    
    if not __debug__:
        print('own_track position')
        for i in result.owntrack_pos:
            print(i)
    
    plt.show()
