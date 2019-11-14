# -*- coding: utf-8 -*-
from time import sleep

def test_hedge():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    #V.mem['timestamp'] = str(time.time())
    from parts import Timestamp
    V.add(Timestamp(), outputs=['timestamp'])

    from parts import HedgehogController
    hedge = HedgehogController(debug=True)
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

    '''
            return self.usnav_id, self.usnav_x, self.usnav_y, self.usnav_z, \
            self.usnav_angle, self.usnav_timestamp, \
            self.imu_x, self.imu_y, self.imu_z, \
            self.imu_qw, self.imu_qx, self.imu_qy, self.imu_qz, \
            self.imu_vx, self.imu_vy, self.imu_vz, \
            self.imu_ax, self.imu_ay, self.imu_az, \
            self.imu_gx, self.imu_gy, self.imu_gz, \
            self.imu_mx, self.imu_my, self.imu_mz, \
            self.imu_timestamp, \
            self.dist_id, self.dist_b1, self.dist_b1d, self.dist_b2, self.dist_b2d, \
            self.dist_b3, self.dist_b3d, self.dist_b4, self.dist_b4d, \
            self.dist_timestamp
    '''

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
        V.start(rate_hz=20, max_loop_count=10000)
    finally:
        print('stop')
        
def test_imu():
    import donkeycar as dk
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    '''
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
    ], threaded=False)
    '''

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
        ak8963_address=cfg.AK8965_I2C_ADDRESS, 
        debug=True)
    V.add(imu,
        outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
            'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z', 'imu/temp',
            'imu/recent', 'imu/mpu_timestamp'],
        threaded=False)

    '''
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
    '''

    '''
    from parts.sensors.imu import PrintMpu9250
    V.add(PrintMpu9250(), inputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z', 'imu/temp',
        'imu/recent', 'imu/mpu_timestamp'
    ])
    '''

    try:
        V.start(rate_hz=20, max_loop_count=1000)
    except KeyboardInterrupt:
        pass
    finally:
        if pgio.connected:
            pgio.stop()


if __name__ == '__main__':
    #test_hedge()
    test_imu()