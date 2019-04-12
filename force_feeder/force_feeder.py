from __future__ import print_function
import sys
import time
import serial
import math
import matplotlib
import matplotlib.pyplot as plt
import signal
import yaml

from led_scheduler import LedScheduler
from highpass_filter import HighpassFilter
from delay_threshold import DelayThreshold


class ForceFeeder(serial.Serial):

    ResetSleepDt = 0.5
    Baudrate = 115200
    Timeout = 10.0

    def __init__(self,config_filename):
        with open(config_filename,'r') as f:
            self.params = yaml.load(f)
        serial_params = {'baudrate': self.Baudrate, 'timeout': self.Timeout}
        super(ForceFeeder,self).__init__(self.params['ports']['loadcell'], **serial_params)
        time.sleep(self.ResetSleepDt)

        self.t_init =  time.time()
        self.t_list = []
        self.force_list = []
        self.filt_force_list = []

        self.use_highpass = self.params['highpass_filter']['enabled'] 
        self.high_pass_filter = HighpassFilter(fcut=self.params['highpass_filter']['cutoff_freq'])
        self.led_scheduler = LedScheduler(self.params)
        self.delay_threshold = DelayThreshold(self.params['threshold'])

        self.running = False
        signal.signal(signal.SIGINT, self.sigint_handler)

        plt.ion()
        self.fig = plt.figure(1)
        self.ax = plt.subplot(111) 
        thresh_line_x = [0,self.params['window']['size_t']]
        thresh_line_y = [self.params['threshold']['value'], self.params['threshold']['value']]
        self.thresh_line, = plt.plot(thresh_line_x, thresh_line_y, 'k') 
        self.force_line, = plt.plot([0,1], [0,1],'b')
        plt.grid('on')
        plt.xlabel('(sec)')
        plt.ylabel('(V)')
        self.ax.set_xlim(0,self.params['window']['size_t'])
        self.ax.set_ylim(-0.1,self.params['window']['size_f'])
        plt.title("Force Sensor  (Type=AE801)")
        self.force_line.set_xdata([])
        self.force_line.set_ydata([])
        self.fig.canvas.flush_events()


    def sigint_handler(self,signum,frame):
        self.running = False

    def run(self):

        self.write('b\n')
        self.running = True

        with open(self.params['data_file'], 'w') as fid:
            while self.running:
                have_data = False
                #while self.in_waiting > 0:
                while self.inWaiting() > 0:
                    # Not the best - throwing some points away. 
                    # Maybe put points in list, process later. 
                    line = self.readline()
                    have_data = True
                    #print('.',end='')
                #print()

                if have_data:
                    line = line.strip()
                    data = line.split(' ')
                    try:
                        t = float(data[0])
                        force = abs(float(data[1])) # arbitrary units
                    except IndexError:
                        continue
                    except ValueError:
                        continue
                    #print('{0:0.2f}, {1:0.2f}'.format(t,force))

                    t_elapsed = time.time() - self.t_init
                    self.t_list.append(t_elapsed)

                    if len(self.t_list) < 2:
                        dt = None
                    else:
                        dt = self.t_list[-1] - self.t_list[-2]

                    self.force_list.append(force)
                    filt_force = self.high_pass_filter.update(force,dt)
                    self.filt_force_list.append(filt_force)


                    # Check if force (or filtered force) is above threshold and update led scheduler
                    if self.use_highpass:
                        force_tmp = filt_force
                    else:
                        force_tmp = force
                    #above_threshold = force_tmp > self.params['threshold']['value']

                    above_threshold = self.delay_threshold.update(t_elapsed,force_tmp)
                    self.led_scheduler.update(t_elapsed, above_threshold)

                    while (self.t_list[-1] - self.t_list[0]) > self.params['window']['size_t']:
                        self.t_list.pop(0)
                        self.force_list.pop(0)
                        self.filt_force_list.pop(0)

                    self.force_line.set_xdata(self.t_list)
                    if self.use_highpass:
                        self.force_line.set_ydata(self.filt_force_list)
                    else:
                        self.force_line.set_ydata(self.force_list)

                    thresh_line_x = [self.t_list[0], max(self.t_list[-1],self.params['window']['size_t'])]
                    thresh_line_y = [self.params['threshold']['value'], self.params['threshold']['value']]
                    self.thresh_line.set_xdata(thresh_line_x)
                    self.thresh_line.set_ydata(thresh_line_y)

                    xmin = self.t_list[0]
                    xmax = max(self.params['window']['size_t'], self.t_list[-1])

                    self.ax.set_xlim(xmin,xmax)
                    self.fig.canvas.flush_events()
                    plt.pause(0.0001)
                    fid.write('{0} {1} {2}\n'.format(t_elapsed, force, int(self.led_scheduler.value)))

        print('quiting')
        self.write('\n')




# ---------------------------------------------------------------------------------------
if __name__ == '__main__':


    feeder= ForceFeeder(sys.argv[1])
    feeder.run()



