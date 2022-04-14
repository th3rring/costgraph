import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
from costgraph.Functions import *
from costgraph.Constants import *
from costgraph.Graph import *

def graphEdgeFunc(title: str, edge: EdgeCostFunction):
    
    title_fontsize = 25
    equation_fontsize = 24
    fontsize=20
    
    padding = 0.2
    
    # Turn on TEX support
    plt.rcParams['text.usetex'] = True
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.set_facecolor((1,1,1))
    
    # Generate plot
    BB = np.linspace(0, 1.5 * (edge.b_min), 500)
    C = edge.f(BB)
    ax.plot(BB, C, label=edge.equation)
    
    # Set plot limits
    ylim_bottom = 0.8 * edge.c_min
    ylim_top = 1.5 * edge.c_init
    ylim_diff = ylim_top - ylim_bottom
    
    xlim_bottom = 0
    xlim_top = 1.3 * edge.b_min
    xlim_diff = xlim_top - xlim_bottom
    
    # Display equation
    #ax.text(0.5 * xlim_diff + xlim_bottom, 0.8 * ylim_diff + ylim_bottom, edge.equation, fontsize=equation_fontsize)
    
    # Display points
    ax.text(edge.b_init + padding, edge.c_init + padding, 
            r"$(c_{init}=%10.2f, b_{init}=%10.2f)$" % (edge.c_init, edge.b_init), fontsize=fontsize)
    ax.text(edge.b_min - 2 * padding, edge.c_min + 2 * padding, 
            r"$(c_{min}=%10.2f, b_{min}=%10.2f)$" % (edge.c_min, edge.b_min), fontsize=fontsize)
    
    # Print extra parameters for complex models
    if isinstance(edge, EdgeCostExponential):
        # This is a trick to display the alpha value in the legend.
        ax.plot([],[], ' ', label=r"$\alpha = %10.2f$" % edge.alpha)
        
    
    # Mark important points
    color=['dimgray', 'darkgray']
    x_pts = [edge.b_init, edge.b_min]
    y_pts = [edge.c_init, edge.c_min]
    plt.hlines(y=y_pts, xmin=[0,0], 
               xmax=x_pts, color=color, linestyles='dashed')
    plt.vlines(x=x_pts, ymin=[ylim_bottom, ylim_bottom], 
               ymax=y_pts, color=color, linestyle = 'dashed')
    
     # Set plot settings
    plt.legend(frameon=False, fontsize=equation_fontsize)
    plt.ylim(ylim_bottom, ylim_top)
    plt.xlim(xlim_bottom, xlim_top)
    ax.set_title(title, fontsize=title_fontsize)
    ax.set_xlabel("Edge budget", fontsize=fontsize)
    ax.set_ylabel("Cost of Edge Traversal", fontsize=fontsize)
    plt.show()

def generateEdgeFuncImg(edge: EdgeCostFunction, b: float):
    
    # Turn on TEX support
    plt.rcParams['text.usetex'] = True

    fontsize = 15
    fig, ax = plt.subplots(figsize=(4, 2.5))
    fig.set_facecolor((1,1,1))
    
    # Generate plot
    b_total = 1.5 * edge.b_min
    n = 500

    # Set plot limits
    ylim_bottom = 0.8 * edge.c_min
    ylim_top = 1.5 * edge.c_init
    
    xlim_bottom = 0
    xlim_top = 1.3 * edge.b_min

    BB = np.linspace(0, b_total, n)
    C = edge.f(BB)
    ax.plot(BB, C, lw=2, label=r"$(b=%10.2f, c=%10.2f)$" % (b , edge.f(b)))

    b_index = int(n * (b/b_total))
    plt.fill_between(BB[0:b_index],0,C[0:b_index],color='gray')
    
     # Set plot settings
    plt.ylim(ylim_bottom, ylim_top)
    plt.xlim(xlim_bottom, xlim_top)

    cur_xticks = ax.get_xticks()
    plt.xticks([cur_xticks[0], cur_xticks[-1]], visible=True, rotation="horizontal", fontsize=fontsize)
    cur_yticks = ax.get_yticks()
    plt.yticks([cur_yticks[0], cur_yticks[-1]], visible=True, rotation="horizontal", fontsize=fontsize)

    leg = ax.legend(handlelength=0, handletextpad=0, frameon=False, fontsize=fontsize)
    for item in leg.legendHandles:
        item.set_visible(False)

    return plt

def showEdgeFuncImg(edge: EdgeCostFunction, b: float):

    plt = generateEdgeFuncImg(edge, b)
    plt.show()

def saveEdgeFuncImg(filename: str, edge: EdgeCostFunction, b: float, format='svg'):

    plt = generateEdgeFuncImg(edge, b)
    plt.savefig(filename, format=format, bbox_inches='tight')

def printDir(p):
    for i in p.iterdir():
        print(i)

def saveGraphImgs(g: CostFuncGraph, s_path, format='svg'):

    g.label_path(s_path)

    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    project_dir = source_dir.parent
    edgecost_dir = project_dir.joinpath(IMAGE_DIR).joinpath(EDGECOSTFUNC_IMAGE_DIR)

    for e in s_path:
        img_filepath = edgecost_dir.joinpath(f"{e.u}-{e.v}")
        saveEdgeFuncImg(img_filepath, g.get_function(e.u, e.v), e.b, format=format)
        g.label_edge_image(e.u, e.v, str(img_filepath) + "." + format)

