# -*- coding: utf-8 -*-
from time import sleep

def test_hedge():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()


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
        'imu/gx', 'imu/gy', 'imu/gz',
        'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp'
        'dist/id',
        'dist/b1', 'dist/b1d',
        'dist/b2', 'dist/b2d',
        'dist/b3', 'dist/b3d',
        'dist/b4', 'dist/b4d',
        'dist/timestamp',
    ])
    from parts.broker.debug import PrintUSNav
    usnav = PrintUSNav()
    V.add(usnav, inputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
    ])

    from parts.broker.debug import PrintIMU
    imu = PrintIMU()
    V.add(imu, inputs=[
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz',
        'imu/mx', 'imu/my', 'imu/mz',
        'imu/timestamp',
    ])

    from parts.broker.debug import PrintDist
    dist = PrintDist()
    V.add(dist, inputs=[
        'dist/id',
        'dist/b1', 'dist/b1d',
        'dist/b2', 'dist/b2d',
        'dist/b3', 'dist/b3d',
        'dist/b4', 'dist/b4d',
        'dist/timestamp',
    ])
    try:
        V.start(rate_hz=20, max_loop_count=10000)
    finally:
        print('stop')
        


if __name__ == '__main__':
    test_hedge()
