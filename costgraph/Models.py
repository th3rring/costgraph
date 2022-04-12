import logging
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from dataclasses import dataclass

@dataclass
class PathEdge():
    """ Class for keeping track of shortest path edges """
    u: str
    v: str
    b: float
    c: float

    def __repr__(self):
        return f'{self.u} -> {self.v}: b={self.b:.5f} c={self.c:.5f}'


class Model():

    def __init__(self, graph, start, target, budget, approx_res, verbose=False):
        self._graph = graph
        self._start = start
        self._target = target
        self._budget = budget
        self._approx_res = approx_res
        self.verbose = verbose

        # Set a hardcoded slack beyond the b_min to sample up to
        self._slack = 2

        # Build a model with these parameters
        self._buildModel()

    def _buildModel(self):
        self._gp_model = gp.Model('model')

        if not self.verbose:
            self._gp_model.setParam('OutputFlag', 0)

        # Create Gurobi dicts for the graph
        self._arcs, self._costs = gp.multidict(((u, v), d["f"]) for (u, v, d) in self._graph.edges(data=True))

        # Make decision variables
        self._x = self._gp_model.addVars(self._arcs, vtype=GRB.BINARY, name ="path")
        self._b = self._gp_model.addVars(self._arcs, vtype=GRB.CONTINUOUS, ub=self._budget, name="budget")
        self._f = self._gp_model.addVars(self._arcs, vtype=GRB.CONTINUOUS, name="aux_f")

        # Construct piecewise linear approximation of edge cost functions
        for (u, v) in self._costs:

            # Get current b_min
            b_min = self._costs.select(u,v)[0].b_min

            # Construct linspace up to b_min + slack
            budget_pts = np.linspace(0, b_min + self._slack, self._approx_res)

            # Get cost for each point in the linspace
            cost_pts = self._costs.select(u,v)[0].f(budget_pts)

            # Add a PWL constraint between an aux_f variable and this cost linspace
            self._gp_model.addGenConstrPWL(self._b[u,v], self._f[u,v], budget_pts, cost_pts)

        # Objective function
        self._gp_model.setObjective(
            gp.quicksum(
                self._f[u,v]  * self._x[u,v] for (u, v) in self._graph.edges), GRB.MINIMIZE)

        # Flow constraint
        for i in self._graph.nodes:
            self._gp_model.addConstr( gp.quicksum(self._x[i,j] for i,j in self._arcs.select(i, '*')) - gp.quicksum(self._x[j,i] for j,i in self._arcs.select('*',i)) == 
                             (1 if i==self._start else -1 if i==self._target else 0 ),'node%s_' % i )

        # Budget constraint
        self._gp_model.addConstr(gp.quicksum(self._b[u,v]*self._x[u,v] for (u,v) in self._graph.edges) <= self._budget)

        # Rank constraint
        for i in self._graph.nodes:
            self._gp_model.addConstr(gp.quicksum(self._x[u,v] for u,v in self._arcs.select(i, "*")) <= 1)

    def solve(self, print_path=False):
        self._gp_model.optimize()

        if self._gp_model.status == GRB.Status.OPTIMAL:

            shortest_path = []
            total_cost = 0
            total_budget = 0

            for i,j in self._arcs:
                if self._x[i,j].x > 0:

                    b_cur = self._b[i,j].x
                    total_budget += b_cur

                    c_cur = self._costs.select(i,j)[0].f(b_cur)
                    total_cost += c_cur

                    shortest_path.append(PathEdge(i, j, b_cur, c_cur))

            logging.info("Shortest path found!")

            if print_path:
                for e in shortest_path:
                    print(e)
                print(f"Total budget used: {total_budget}")
                print(f"Total cost for path: {total_cost:.5f}")

            return shortest_path

        else:
            logging.error(f"Gurobi Error {self._gp.model.status}")
            return None
