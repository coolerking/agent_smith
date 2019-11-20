# -*- coding: utf-8 -*-
from time import sleep

def test_joy_sub(use_debug=True):
    import donkeycar as dk
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/tom.yml', 'tom')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=use_debug)
    print('on')
    power.on()


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

    # ダミー Tub image
    from parts.broker.debug import GetImage
    image = GetImage()
    V.add(image, outputs=['cam/image_array'])

    from parts import get_js_controller
    ctr = get_js_controller(cfg)
    V.add(ctr, 
            inputs=['cam/image_array'],
            outputs=joystick_items,
            threaded=True)
    
    # Publisher
    from parts.broker.pub import JoystickPublisher
    pub_joy = JoystickPublisher(factory, debug=use_debug)
    V.add(pub_joy, inputs=joystick_items)

    class PrintJoystick:
        def run(self, an, th, lth, mode, rec):
            print('[Pub]{} angle:{}, throttle:{} lift:{} rec:{}'.format(
                str(mode), str(an), str(th), str(lth), str(rec)
            ))
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