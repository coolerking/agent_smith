# -*- coding: utf-8 -*-
from time import sleep


def test_pub():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    # Tub json
    '''
    from parts.broker.debug import GetTub
    tub = GetTub()
    V.add(tub, outputs=[
        'user/mode',
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'timestamp'
    ])
    '''
    tubs = [
        #'user/mode',
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode',
    ]
    V.mem['user/mode'] = 'user'
    value = 0.0
    for key in tubs:
        value = value + 1.0
        V.mem[key]=value
        print('key:{} value:{}'.format(key, str(value)))
    
    # Tub image
    from parts.broker.debug import GetImage
    image = GetImage()
    V.add(image, outputs=['cam/image_array'])

    # mpu
    '''
    from parts.broker.debug import GetMpu
    mpu = GetMpu()
    V.add(mpu, outputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp', 'imu/mpu_timestamp'
    ])
    '''
    mpus = [
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp', 'imu/mpu_timestamp'
    ]
    value = 0.0
    for key in mpus:
        value = value + 1.0
        V.mem[key]=value
        print('key:{} value:{}'.format(key, str(value)))
    V.mem['imu/recent'] = '{}'

    '''
    from parts.broker.debug import GetHedge
    hedge = GetHedge()
    V.add(hedge, outputs=[
        # USNav 6
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
        # IMU 20
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
        # USNav Raw 10
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
    ])
    '''
    hedges = [
        # USNav 6
        #'usnav/id',
        'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
        # IMU 20
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
        # USNav Raw 10
        #'dist/id', 'dist/b1', 
        'dist/b1d', 
        #'dist/b2', 
        'dist/b2d', 
        #'dist/b3', 
        'dist/b3d', 
        #'dist/b4', 
        'dist/b4d', 'dist/timestamp',
    ]
    value = 0.0
    for key in hedges:
        value = value + 1.0
        V.mem[key]=value
        print('key:{} value:{}'.format(key, str(value)))
    
    hedges_str = [
        'usnav/id',
        # USNav Raw 10
        'dist/id', 'dist/b1', 
        'dist/b2', 
        'dist/b3', 
        'dist/b4', 
    ]
    for i in range(len(hedges_str)):
        V.mem[hedges_str[i]] = str(i+1)
        print('key:{} value:{}'.format(hedges_str[i], str(i+1)))
    
    # Publisher

    from parts.broker.pub import Publisher
    pub = Publisher(factory, debug=False)
    V.add(pub, inputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode',
    ])

    '''
    from parts.broker.pub import UserPublisher
    tub_pub = UserPublisher(factory, debug=False)
    V.add(tub_pub, inputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'user/mode'
    ])
    '''

    
    from parts.broker.pub import ImagePublisher
    image_pub = ImagePublisher(factory, debug=True)
    V.add(image_pub, inputs=[
        'cam/image_array',
    ])

    
    from parts.broker.pub import USNavPublisher
    usnav = USNavPublisher(factory, debug=True)
    V.add(usnav, inputs=[
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
    ])

    from parts.broker.pub import USNavRawPublisher
    usnav_raw = USNavRawPublisher(factory, debug=True)
    V.add(usnav_raw, inputs=[
        # USNav Raw
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
    ])

    from parts.broker.pub import IMUPublisher
    imu = IMUPublisher(factory, debug=True)
    V.add(imu, inputs=[
        # IMU
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
    ])

    from parts.broker.pub import Mpu9250Publisher
    mpu = Mpu9250Publisher(factory, debug=True)
    V.add(mpu, inputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp',
        'imu/recent', 'imu/mpu_timestamp',
    ])

    from parts.broker.pub import Mpu6050Publisher
    mpu = Mpu6050Publisher(factory, debug=True)
    V.add(mpu, inputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        #'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        #'imu/temp',
        'imu/recent', 'imu/mpu_timestamp',
    ])
    

    try:
        V.start(rate_hz=20, max_loop_count=1000)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(3)


if __name__ == '__main__':
    test_pub()
