import lark
from lark import Lark, Transformer, v_args, exceptions
import sys
import matplotlib.pyplot as plt
from matplotlib import rcParams

# https://qiita.com/yniji/items/3fac25c2ffa316990d0c matplotlibで日本語を使う
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

import mapinterpleter as interp
import mapplot

if __name__ == '__main__':
    rule = open('map-grammer.lark', encoding='utf-8').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    interpreter = interp.ParseMap(None,parser)
    
    argvs = sys.argv
    
    try:
        result = interpreter.load_files(argvs[1])
    except exceptions.VisitError as e:
        print(e.orig_exc)
        #print(vars(e))
        #print(e)
        sys.exit()
    except Exception as e:
        print('Unexpected error.')
        #print(type(e))
        print(e)
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
        
    dmin = min(result.station.position.keys()) - 500
    dmax = max(result.station.position.keys()) + 500
        
    mplot = mapplot.Mapplot(result)
    
    planer_fig = plt.figure()
    ax1 = planer_fig.add_subplot(1,1,1)
    
    profile_fig = plt.figure()
    ax2 = profile_fig.add_subplot(2,1,1)
    ax3 = profile_fig.add_subplot(2,1,2)
    
    mplot.plane(ax1,distmin=dmin,distmax=dmax)
    mplot.vertical(ax2, ax3,distmin=dmin,distmax=dmax)
    mplot.stationpoint_plane(ax1)
    mplot.stationpoint_height(ax2)
    mplot.gradient_value(ax2)
    mplot.radius_value(ax3)
    
    if not __debug__:
        print('own_track position')
        for i in result.owntrack_pos:
            print(i)
    
    plt.show()
