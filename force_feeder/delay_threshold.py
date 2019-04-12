from __future__ import print_function

class DelayThreshold(object):

    def __init__(self,params):
        self.params = dict(params)
        self.t_list = []
        self.x_list = []

    def update(self, t, x):
        self.t_list.append(t)
        self.x_list.append(x)
        while (t - self.t_list[0]) > self.params['window']:
            self.t_list.pop(0)
            self.x_list.pop(0)
        test = True
        for item in self.x_list:
            if item < self.params['value']:
                test = False
        return test




