import lark
from lark import Lark, Transformer, v_args
import sys
import matplotlib.pyplot as plt

import mapinterpleter as interp
import mapplot

if __name__ == '__main__':
    rule = open('map-grammer.lark').read()
    parser = Lark(rule, parser='lalr', maybe_placeholders=True)
    interpreter = interp.ParseMap(None,parser)
    
    argvs = sys.argv
    
    result = interpreter.load_files(argvs[1])
    
    print(result.own_track.data)
    
    planer_fig = plt.figure()
    profile_fig = plt.figure()
    ax1 = planer_fig.add_subplot(1,1,1)
    ax2 = profile_fig.add_subplot(2,1,1)
    ax3 = profile_fig.add_subplot(2,1,2)
    mapplot.plot_planer_map(result.own_track.data, ax1)
    mapplot.plot_vetical_profile(result.own_track.data, ax2, ax3)
    plt.show()
