# -*- coding: utf-8 -*-
from time import sleep


user_items = [
    'user/angle', 'user/throttle', 'user/lift_throttle', 'user/mode',
]
user_types = [
    'float', 'float', 'float', 'str',
]
joystick_items = []
joystick_types = []
joystick_items += user_items
joystick_types += user_types
joystick_items += ['recording']
joystick_types += ['boolean']

class PrintJoystick:
    def run(self, an, th, lth, mode, rec):
        print('[JOY]({}) angle:{}, throttle:{} lift:{} rec:{}'.format(
            str(mode), str(an), str(th), str(lth), str(rec)
        ))


def test_joy_sub(use_debug=True):
    import donkeycar as dk
    #cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/jones.yml', 'jones')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=use_debug)
    print('on')
    power.on()

    from parts.broker.sub import JoystickSubscriber
    sub_joy = JoystickSubscriber(factory, debug=use_debug)
    V.add(sub_joy, outputs=joystick_items)
    
    
    V.add(PrintJoystick(), inputs=joystick_items)

    try:
        V.start(rate_hz=20, max_loop_count=10000)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(5)

if __name__ == '__main__':
    test_joy_sub()