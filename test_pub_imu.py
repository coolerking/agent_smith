# -*- coding: utf-8 -*-

def test_pub_imu():
    
    try:
        import donkeycar as dk
        import pigpio
    except:
        raise
    pgio = pigpio.pi()
    if not pgio.connected:
        raise RuntimeError('cannot connect pigpiod')
    
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    from parts.sensors.imu import Mpu9250
    imu = Mpu9250(
        pgio=pgio,
        bus=cfg.MPU9250_I2C_BUS, 
        mpu9250_address=cfg.MPU9250_I2C_ADDRESS, 
        ak8963_address=cfg.AK8963_I2C_ADDRESS,
        depth=cfg.MPU9250_DEPTH,
        debug=True)
    V.add(imu,
        outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
            'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z', 'imu/temp',
            'imu/recent', 'imu/mpu_timestamp'
        ])

    from parts import HedgehogController
    hedge = HedgehogController(debug=False)
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
    ])

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')
    from parts.broker import HedgePublisher
    pub = HedgePublisher(factory, debug=True)
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

    from parts.broker import Mpu9250Publisher
    m_pub = Mpu9250Publisher(factory, debug=True)
    V.add(m_pub, inputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z', 'imu/temp',
        'imu/recent', 'imu/mpu_timestamp'
    ])

    try:
        V.start(rate_hz=20, max_loop_count=10000)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            factory.disconnect()
        except:
            print('ignore raise exception during aws factory disconnecting')
        if pgio.connected:
            pgio.stop()

if __name__ == '__main__':
    test_pub_imu()