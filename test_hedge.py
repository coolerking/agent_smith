# -*- coding: utf-8 -*-
from time import sleep

def test_hedge():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts import HedgeHogController
    hedge = HedgeHogController(debug=True)
    V.add(hedge, outputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'dist_id',
        'dist_b1', 'dist_b1d',
        'dist_b2', 'dist_b2d',
        'dist_b3', 'dist_b3d',
        'dist_b4', 'dist_b4d',
        'dist_timestamp'
    ])
    from parts.broker.debug import PrintUSNav
    usnav = PrintUSNav()
    V.add(usnav, inputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp'
    ])

    from parts.broker.debug import PrintIMU
    imu = PrintIMU()
    V.add(imu, inputs=[
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
    ])

    from parts.broker import HedgePublisher
    hedge_pub = HedgePublisher(factory, debug=True)
    V.add(hedge_pub, inputs=[
                'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'dist_id',
        'dist_b1', 'dist_b1d',
        'dist_b2', 'dist_b2d',
        'dist_b3', 'dist_b3d',
        'dist_b4', 'dist_b4d',
        'dist_timestamp', 'timestamp'
    ])

    try:
        V.start(rate_hz=20, max_loop_count=1000)
    finally:
        print('stop')
        


if __name__ == '__main__':
    test_hedge()
