from led_pwm_control import LEDController 
import rospy

class LedScheduler(object):

    def __init__(self, params) :
        self.params = dict(params)
        self.led_on = False 
        self.last_on_t  = -self.total_stimulus_dt
        self.activation_count = 0

        self.dev = LEDController(params['ports']['ledpwm'])
        self.turn_off_led()

    def __del__(self):
        self.turn_off_led()

    @property
    def value(self):
        if self.led_on:
            rval = self.params['stimulus']['on_value']
        else:
            rval = self.params['stimulus']['off_value']
        return rval

    @property
    def total_stimulus_dt(self):
        return self.params['stimulus']['on_dt'] + self.params['stimulus']['off_dt']
    
    def turn_on_led(self,t):
        if not self.led_on:
            self.dev.set_value(self.params['stimulus']['pin'], self.params['stimulus']['on_value'])
            self.activation_count += 1
            self.led_on = True
            self.last_on_t = t

    def turn_off_led(self):
        if self.led_on:
            self.dev.set_value(self.params['stimulus']['pin'], self.params['stimulus']['off_value'])
            self.led_on = False

    def update(self, t, test_val): 
        if self.led_on:

            if self.params['stimulus']['off_dt'] <= 0.0:
                if not test_val:
                    self.turn_off_led()
                    print('led off')
            else:
                if (t - self.last_on_t) > self.params['stimulus']['on_dt']:
                    self.turn_off_led()
                    print('led off')
        else:
            if test_val:
                if (t - self.last_on_t) > self.total_stimulus_dt: 
                    self.turn_on_led(t)   
                    print('led on')





