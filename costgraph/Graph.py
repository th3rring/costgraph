import networkx as nx
import pydot as pd
from costgraph.Functions import EdgeCostFunction
from costgraph.Models import ShortestPath, PathEdge

class CostFuncGraph(nx.DiGraph):

    def __init__(self, *args, **kwargs):
        super(CostFuncGraph, self).__init__(*args, **kwargs)

    def add_edge(self, u, v, func: EdgeCostFunction):
        if not (isinstance(func, EdgeCostFunction) or issubclass(type(func), EdgeCostFunction)):
            raise Exception(f"Wrong type for edges: {type(func)}")
        super(CostFuncGraph, self).add_edge(u,v, f=func)

    def set_function(self, u, v, func: EdgeCostFunction):
       self.add_edge(u,v,func)

    def set_functions(self, edges, func: EdgeCostFunction):
        for (u,v) in edges:
            self.set_function(u,v,func)
    
    def get_function(self, u, v):
        return self.get_edge_data(u,v)["f"]

    def is_valid(self):
        
        # Return false if any edge does not have a function
        for (u,v,d) in self.edges(data=True):
            if "f" not in d.keys():
                return False

        return True

    def annotate_edge(self, u, v, b: float, c: float):
        # TODO Test if this overrides the existing f=func attribute on each edge
        super(CostFuncGraph, self).add_edge(u,v,b=b,c=c)
    
    def annotate_path(self, path: ShortestPath):
        for e in path:
            self.annotate_edge(e.u, e.v, e.b, e.c)

    def label_path(self, path: ShortestPath):
        self.annotate_path(path)

        for e in path:
            self.annotate_edge(e.u, e.v, e.b, e.c)
            super(CostFuncGraph, self).add_edge(e.u,e.v,label="""<<TABLE 
            BORDER="0"
            >
            <TR><TD><IMG SRC="{}"/></TD></TR>
            </TABLE>>""")

    def label_edge_image(self, u, v, filepath):
        cur_label = self.get_edge_data(u,v)["label"]
        super(CostFuncGraph, self).add_edge(u, v, label=cur_label.format(filepath))

    def toDot(self):
        return nx.drawing.nx_pydot.to_pydot(self)

