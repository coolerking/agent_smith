# -*- coding: utf-8 -*-
from donkeycar.parts.controller import Joystick, JoystickController


class F710ForkliftJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.button_names = {
            # from wizard
            0x130 : 'A',
            0x131 : 'B',
            0x133 : 'X',
            0x134 : 'Y',
            0x136 : 'L1',
            0x137 : 'R1',
            0x13a : 'back', # 反応なし！
            0x13b : 'start',
            0x13c : 'logo',
            0x13d : 'L3',
            0x13e : 'R3',
        }


        self.axis_names = {
            # from wizard
            0x10 : 'dpad_leftright', # 1 is right, -1 is left
            0x11 : 'dpad_updown', # 1 is down, -1 is up

            0x2 : 'L2',
            0x5 : 'R2',

            0x0 : 'left_stick_horz',
            0x1 : 'left_stick_vert',
            0x3 : 'right_stick_horz',
            0x4 : 'right_stick_vert',
        }

class ForkliftJoystickController(JoystickController):
    def __init__(self,
    poll_delay=0.0,
    throttle_scale=1.0,
    steering_scale=1.0,
    lift_throttle_scale=1.0,
    throttle_dir=-1.0,
    lift_throttle_dir=-1.0,
    dev_fn='/dev/input/js0',
    auto_record_on_throttle=True):
        super().__init__(poll_delay, 
        throttle_scale, steering_scale, throttle_dir, dev_fn, auto_record_on_throttle)
        self.lift_throttle = 0.0
        self.lift_throttle_scale = lift_throttle_scale
        self.lift_throttle_dir = lift_throttle_dir
        self.last_lift_throttle_axis_val = 0
        self.constant_lift_throttle = False

    def on_throttle_changes(self):
        '''
        turn on recording when non zero lift throttle in the user mode.
        '''
        if self.auto_record_on_throttle:
            self.recording = ((abs(self.throttle) > self.dead_zone or abs(self.lift_throttle) > self.dead_zone) and self.mode == 'user')

    def emergency_stop(self):
        super().emergency_stop()
        self.lift_throttle = 0.0

    def set_lift_throttle(self, axis_val):
        #this value is often reversed, with positive value when pulling down
        self.last_lift_throttle_axis_val = axis_val
        self.lift_throttle = (self.lift_throttle_dir * axis_val * self.lift_throttle_scale)
        #print("throttle", self.throttle)
        self.on_throttle_changes()

    def increase_max_lift_throttle(self):
        '''
        increase lift throttle scale setting
        '''
        self.lift_throttle_scale = round(min(1.0, self.lift_throttle_scale + 0.01), 2)
        if self.constant_lift_throttle:
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        else:
            self.lift_throttle = (self.lift_throttle_dir * self.last_lift_throttle_axis_val * self.lift_throttle_scale)

        print('lift_throttle_scale:', self.lift_throttle_scale)

    def increase_max(self):
        super().increase_max_throttle()
        self.increase_max_lift_throttle()

    def decrease_max_lift_throttle(self):
        '''
        decrease lift throttle scale setting
        '''
        self.lift_throttle_scale = round(max(0.0, self.lift_throttle_scale - 0.01), 2)
        if self.constant_lift_throttle:
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        else:
            self.lift_throttle = (self.lift_throttle_dir * self.last_lift_throttle_axis_val * self.lift_throttle_scale)

        print('lift_throttle_scale:', self.lift_throttle_scale)

    def decrease_max(self):
        super().decrease_max_throttle()
        self.decrease_max_lift_throttle()

    def toggle_constant_lift_throttle(self):
        '''
        toggle constant lift throttle
        '''
        if self.constant_lift_throttle:
            self.constant_lift_throttle = False
            self.lift_throttle = 0
            self.on_throttle_changes()
        else:
            self.constant_lift_throttle = True
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        print('constant_lift_throttle:', self.constant_lift_throttle)
    
    def toggle_constant(self):
        super().toggle_constant_throttle()
        self.constant_lift_throttle()
    
    def run_threaded(self, img_arr=None):
        '''
        process E-Stop state machine
        '''
        if self.estop_state > self.ES_IDLE:
            if self.estop_state == self.ES_START:
                self.estop_state = self.ES_THROTTLE_NEG_ONE
                return 0.0, -1.0 * self.throttle_scale,  0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_NEG_ONE:
                self.estop_state = self.ES_THROTTLE_POS_ONE
                return 0.0, 0.01, 0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_POS_ONE:
                self.estop_state = self.ES_THROTTLE_NEG_TWO
                self.throttle = -1.0 * self.throttle_scale
                return 0.0, self.throttle, 0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_NEG_TWO:
                self.throttle += 0.05
                if self.throttle >= 0.0:
                    self.throttle = 0.0
                    self.estop_state = self.ES_IDLE
                return 0.0, self.throttle, 0.0, self.mode, False

        if self.chaos_monkey_steering is not None:
            return self.chaos_monkey_steering, self.throttle, self.lift_throttle, self.mode, False

        return self.angle, self.throttle, self.lift_throttle, self.mode, self.recording

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        #return None, None, None, None, None


class F710ForkliftJoystickController(ForkliftJoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug') or False
        super().__init__(*args, **kwargs)
        print('mode is {}'.format(self.mode))

    def init_js(self):
        #attempt to init joystick
        try:
            self.js = F710ForkliftJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls

        self.button_down_trigger_map = {
            'back' : self.toggle_mode, # 動かず
            'start' : self.toggle_constant_throttle,
            'logo' : self.toggle_mode, # self.normal_stop,

            'B': self.toggle_manual_recording,
            'Y': self.erase_last_N_records,
            'A': self.emergency_stop,
            'X': self.normal_stop,

            'R1' : self.chaos_monkey_on_right,
            'L1' : self.chaos_monkey_on_left,

            'R3' : self.normal_stop,
            'L3' : self.normal_stop,
        }

        self.button_up_trigger_map = {
            'R1' : self.chaos_monkey_off,
            'L1' : self.chaos_monkey_off,
        }

        self.axis_trigger_map = {
            'left_stick_horz' : self.set_steering,
            'left_stick_vert' : self.set_throttle,

            'right_stick_horz' : self.set_steering,
            'right_stick_vert' : self.set_lift_throttle,

            'dpad_leftright' : self.set_steering,
            'dpad_updown' : self.set_throttle_half,

            'L2' : self.decrease_max_axis,
            'R2' : self.increase_max_axis,
        }

        if self.debug:
            self.button_down_trigger_map = {
                'back' : self._print_back,
                'start' : self._print_start,
                'logo' : self._print_logo,

                'B': self._print_b,
                'Y': self._print_y,
                'A': self._print_a,
                'X': self._print_x,

                'R1' : self._print_r1,
                'L1' : self._print_l1,

                'R3' : self._print_r3,
                'L3' : self._print_l3,
            }
            self.button_up_trigger_map = {}

            self.axis_trigger_map = {
                'left_stick_horz' : self._print_left_horz,
                'left_stick_vert' : self._print_left_vert,

                'right_stick_horz' : self._print_right_horz,
                'right_stick_vert' : self._print_right_vert,

                'dpad_leftright' : self._print_dpad_horz,
                'dpad_updown' : self._print_dpad_vert,

                'L2' : self._print_l2_axis,
                'R2' : self._print_r2_axis,
            }

    def normal_stop(self):
        super().set_throttle(0.0)
        super().set_steering(0.0)
        super().set_lift_throttle(0.0)


    def increase_max_axis(self, axis_val):
        if self._trim_zero(axis_val) > 0.0:
            super().increase_max()
    
    def decrease_max_axis(self, axis_val):
        if self._trim_zero(axis_val) > 0.0:
            super().decrease_max()
    
    def set_throttle_half(self, axis_val):
        super().set_throttle(axis_val * 0.5)

    def _limit_value(self, val):
        if val > 1.0:
            return 1.0
        elif val < -1.0:
            return -1.0
        else:
            return val

    def _trim_zero(self, val):
        if -0.1 < val and val < 0.1:
            return 0.0
        else:
            return val

    def _inverse_value(self, val):
        inv_val = float((-1.0) * val)
        if inv_val > 1.0:
            return  1.0
        elif inv_val < -1.0:
            return 1.0
        else:
            return inv_val 

    # for debug
    def _print(self, name):
        print('target: {}'.format(str(name)))
    def _print_axis(self, name, axis_val):
        print('target: {} axis_val:{}'.format(str(name), str(axis_val)))
    def _print_l1(self):
        self._print('L1')
    def _print_r1(self):
        self._print('R1')
    def _print_l2_axis(self, axis_val):
        self._print_axis('L2', axis_val)
    def _print_r2_axis(self, axis_val):
        self._print_axis('R2', axis_val)
    def _print_l3(self):
        self._print('L3')
    def _print_r3(self):
        self._print('R3')
    def _print_x(self):
        self._print('X')
    def _print_y(self):
        self._print('Y')
    def _print_a(self):
        self._print('A')
    def _print_b(self):
        self._print('B')
    def _print_back(self):
        self._print('back')
    def _print_start(self):
        self._print('start')
    def _print_logo(self):
        self._print('logo')
    def _print_dpad_vert(self, axis_val):
        self._print_axis('dpad_vert', axis_val)
    def _print_dpad_horz(self, axis_val):
        self._print_axis('dpad_horz', axis_val)
    def _print_left_vert(self, axis_val):
        self._print_axis('left_vert', axis_val)
    def _print_left_horz(self, axis_val):
        self._print_axis('left_horz', axis_val)
    def _print_right_vert(self, axis_val):
        self._print_axis('right_vert', axis_val)
    def _print_right_horz(self, axis_val):
        self._print_axis('right_horz', axis_val)

def get_js_controller(cfg):

    if cfg.CONTROLLER_TYPE == "F710_Forklift":
        cont_class = F710ForkliftJoystickController
        ctr = cont_class(
            throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
            throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
            steering_scale=cfg.JOYSTICK_STEERING_SCALE,
            #steering_dir=cfg.JOYSTICK_STEERING_DIR,
            lift_throttle_dir=cfg.JOYSTICK_LIFT_THROTTLE_DIR,
            lift_throttle_scale=cfg.JOYSTICK_MAX_LIFT_THROTTLE,
            auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
            debug=cfg.JOYSTICK_DEBUG)
        ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
        return ctr
    else:
        try:
            return donkeycar.parts.controller.get_js_controller(cfg)
        except:
            raise