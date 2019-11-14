# -*- coding: utf-8 -*-
from time import sleep

def test_hedge(use_debug=True):
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    #V.mem['timestamp'] = str(time.time())
    from parts import Timestamp
    V.add(Timestamp(), outputs=['timestamp'])

    from parts import HedgehogController
    hedge = HedgehogController(debug=use_debug)
    V.add(hedge, outputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz',
        'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
        'dist/id',
        'dist/b1', 'dist/b1d',
        'dist/b2', 'dist/b2d',
        'dist/b3', 'dist/b3d',
        'dist/b4', 'dist/b4d',
        'dist/timestamp',
    ], threaded=False)

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

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')
    from parts.broker import HedgePublisher
    pub = HedgePublisher(factory)
    V.add(pub, inputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz',
        'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
        'dist/id',
        'dist/b1', 'dist/b1d',
        'dist/b2', 'dist/b2d',
        'dist/b3', 'dist/b3d',
        'dist/b4', 'dist/b4d',
        'dist/timestamp', 'timestamp',
    ])

    try:
        V.start(rate_hz=20, max_loop_count=100)
    finally:
        print('stop')
        
def test_imu(use_debug=True):
    import donkeycar as dk
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    from parts import HedgehogController
    hedge = HedgehogController(debug=use_debug)
    V.add(hedge, outputs=[
        'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z',
        'usnav/angle', 'usnav/timestamp',
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz',
        'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
        'dist/id',
        'dist/b1', 'dist/b1d',
        'dist/b2', 'dist/b2d',
        'dist/b3', 'dist/b3d',
        'dist/b4', 'dist/b4d',
        'dist/timestamp',
    ], threaded=False)

    try:
        import pigpio
    except:
        raise
    pgio = pigpio.pi()
    if not pgio.connected:
        raise RuntimeError('cannot connect pigpiod')

    from parts.sensors.imu import Mpu9250
    imu = Mpu9250(
        pgio=pgio,
        bus=cfg.MPU9250_I2C_BUS, 
        mpu9250_address=cfg.MPU9250_I2C_ADDRESS, 
        ak8963_address=cfg.AK8963_I2C_ADDRESS,
        depth=cfg.MPU9250_DEPTH,
        debug=use_debug)
    V.add(imu,
        outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
            'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z', 'imu/temp',
            'imu/recent', 'imu/mpu_timestamp'])

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

    try:
        V.start(rate_hz=20, max_loop_count=100)
    except KeyboardInterrupt:
        pass
    finally:
        if pgio.connected:
            pgio.stop()


if __name__ == '__main__':
    debug = True
    print('*** test1: hedge and aws')
    test_hedge(use_debug=debug)
    print('*** test1: hedge and mpu9250')
    test_imu(use_debug=debug)