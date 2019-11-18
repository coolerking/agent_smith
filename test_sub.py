# -*- coding: utf-8 -*-
from time import sleep

def test_sub():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/tom.yml', 'tom')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    # Subscriber
    ''''''
    from parts.broker.sub import Subscriber
    sub = Subscriber(factory, debug=False)
    V.add(sub, outputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode', 'timestamp'
    ])
    '''
    from parts.broker.sub import UserSubscriber
    user_sub = UserSubscriber(factory, debug=False)
    V.add(user_sub, outputs=[
        'user/angle', 'user/throttle', 'user/lift_throttle',
        #'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode', 'timestamp'
    ])
    '''

    from parts.broker.sub import ImageSubscriber
    image_sub = ImageSubscriber(factory, debug=False)
    V.add(image_sub, outputs=[
        'cam/image_array',
    ])

    from parts.broker.sub import Mpu9250Subscriber
    mpu_sub = Mpu9250Subscriber(factory, debug=True)
    V.add(mpu_sub, outputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp',
        'imu/mpu_timestamp',
    ])

    from parts.broker.sub import Mpu6050Subscriber
    mpu_sub = Mpu6050Subscriber(factory, debug=True)
    V.add(mpu_sub, outputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        #'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        #'imu/temp',
        'imu/mpu_timestamp',
    ])

    '''
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

    from parts.broker.sub import USNavSubscriber
    usnav_sub = USNavSubscriber(factory, debug=True)
    V.add(usnav_sub, outputs=[
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
    ])

    from parts.broker.sub import USNavRawSubscriber
    usnav_raw_sub = USNavRawSubscriber(factory, debug=True)
    V.add(usnav_raw_sub, outputs=[
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
    ])

    from parts.broker.sub import IMUSubscriber
    imu_sub = IMUSubscriber(factory, debug=True)
    V.add(imu_sub, outputs=[
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
    ])

    try:
        V.start(rate_hz=20, max_loop_count=100)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(20)


if __name__ == '__main__':
    test_sub()
