from __future__ import print_function
import math

class HighpassFilter(object):

    def __init__(self,fcut=1.0):
        self.fcut = fcut
        self.value = None
        self.xlast = None

    def calc_alpha(self, dt):
         return 1.0/(2.0*math.pi*self.fcut + 1.0)

    def update(self, x, dt):
        if self.value is None:
            self.value = x
            self.xlast = x
        else:
            alpha = self.calc_alpha(dt)
            dx = x - self.xlast
            self.value = alpha*(self.value + dx)
            self.xlast = x
        return self.value
