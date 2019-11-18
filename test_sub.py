# -*- coding: utf-8 -*-
from time import sleep

def test_sub():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    # Subscriber

    from parts.broker.sub import Subscriber
    sub = Subscriber(factory, debug=True)
    V.add(sub, inputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode', 'timestamp'
    ])

    '''
    from parts.broker.sub import UserSubscriber
    user_sub = UserSubscriber(factory, debug=True)
    V.add(user_sub, outputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        #'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode', 'timestamp'
    ])
    '''

    from parts.broker.sub import ImageSubscriber
    image_sub = ImageSubscriber(factory, debug=True)
    V.add(image_sub, outputs=[
        'cam/image_array',
    ])

    try:
        V.start(rate_hz=20, max_loop_count=1000)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(20)


if __name__ == '__main__':
    test_sub()
