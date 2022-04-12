import networkx as nx
from costgraph.EdgeFunctions import EdgeCostFunction

class CostFuncGraph(nx.DiGraph):

    def __init__(self, *args, **kwargs):
        super(CostFuncGraph, self).__init__(*args, **kwargs)

    def add_edge(self, u, v, func: EdgeCostFunction):
        if not (isinstance(func, EdgeCostFunction) or issubclass(type(func), EdgeCostFunction)):
            raise Exception(f"Wrong type for edges: {type(func)}")
        super(CostFuncGraph, self).add_edge(u,v, f=func)

