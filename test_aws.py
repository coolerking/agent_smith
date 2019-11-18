# -*- coding: utf-8 -*-
from time import sleep


def test_aws():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    from parts.broker.debug import GetTub
    tub = GetTub()
    V.add(tub, outputs=[
        'user/mode',
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'timestamp'
    ])

    from parts.broker.debug import GetImage
    image = GetImage()
    V.add(image, outputs=['cam/image_array'])

    V.mem['user/mode'] = 'user'

    from parts.broker.pub import Publisher
    pub = Publisher(factory, debug=True)
    V.add(pub, inputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode'
    ])

    from parts.broker.pub import UserPublisher
    tub_pub = UserPublisher(factory, debug=True)
    V.add(tub_pub, inputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'user/mode'
    ])

    from parts.broker.pub import ImagePublisher
    image_pub = ImagePublisher(factory, debug=True)
    V.add(image_pub, inputs=[
        'cam/image_array',
    ])

    try:
        V.start(rate_hz=20, max_loop_count=10000)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(20)

if __name__ == '__main__':
    test_aws()
