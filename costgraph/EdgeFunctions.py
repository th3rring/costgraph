import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB
from abc import ABC, abstractmethod


class EdgeCostFunction(ABC):
    
    def __init__(self, c_init: float, c_min: float, b_init: float, b_min: float):
        self.c_init = c_init
        self.c_min = c_min
        self.b_init = b_init
        self.b_min = b_min
        # If this doesn't work, change this back to a hardcoded value (originally 100)
        # self.infeasible_cost = GRB.INFINITY
        self.infeasible_cost = 100

    @property
    @abstractmethod
    def equation(self):
        """ Return the characteristic equation of the edge function"""

    @abstractmethod
    def f_int(self, b):
        raise NotImplementedError

    def f(self, b) -> float:
        # Output depending on type
        if isinstance(b, np.ndarray):
            return np.array(list(map(self.f_int, b)))
        else:
            return self.f_int(b)
            
class EdgeCostLinear(EdgeCostFunction):

    def __init__(self, c_init: float, c_min: float, b_init: float, b_min: float) -> None:

        # Calculate slope and y-offset with current parameters.
        self.slope =  (c_min - c_init)/(b_min - b_init)
        self.offset =  c_init - self.slope * b_init

        # Call superclass constructor
        super(EdgeCostLinear, self).__init__(c_init, c_min, b_init, b_min)

    @property
    def equation(self):
        return (r"$c = \frac{(c_{min}-c_{init})"
                r"(b - b_{init})}"
                r"{b_{min}-b_{init}}+c_{init}$")


    def f_int(self, b):
        if b < self.b_init:
            return self.infeasible_cost
        
        # Clamp budget to minimum
        if b >= self.b_min:
            return self.c_min
            
        return self.slope*b + self.offset

class EdgeCostExponential(EdgeCostFunction):

    def __init__(self, c_init: float, c_min: float, b_init: float, b_min: float, alpha: float) -> None:

        self.alpha = alpha

        # Call superclass constructor
        super(EdgeCostExponential, self).__init__(c_init, c_min, b_init, b_min)
                
    @property
    def equation(self):
        return  (r"$c = c_{{init}} *"
                         r"e^{-\alpha(b-b_{{init}})} "
                         r"+ c_{{min}}$")

    def f_int(self, b):
        if b < self.b_init:
            return self.infeasible_cost
        
        return self.c_init * np.exp(-self.alpha * (b - self.b_init)) + self.c_min

