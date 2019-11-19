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

    class CheckImageType:
        def run(self, image_array):
            print('[CheckImageType] image_array')
            print(type(image_array))
            print(image_array)
    V.add(CheckImageType(), inputs=[
        'cam/image_array',
    ])

    from parts.broker.sub import Mpu9250Subscriber
    mpu_sub = Mpu9250Subscriber(factory, debug=False)
    V.add(mpu_sub, outputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp',
        'imu/mpu_timestamp',
    ])

    class PrintMpu9250:
        def run(self, ax, ay, az, gx, gy, gz, mx, my, mz, temp, ts):
            print('[Mpu9260] a:({},{},{}) g:({},{},{}) m:({},{},{}) t:{} ts:{}'.format(
                str(ax), str(ay), str(az), str(gx), str(gy), str(gz), str(mx), str(my), str(mz), str(temp), str(ts)
            ))
    V.add(PrintMpu9250(), inputs=[
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp',
        'imu/mpu_timestamp',
    ])

    from parts.broker.sub import Mpu6050Subscriber
    mpu_sub = Mpu6050Subscriber(factory, debug=False)
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

    ''' bug here!'''
    from parts.broker.sub import USNavSubscriber
    usnav_sub = USNavSubscriber(factory, debug=False)
    V.add(usnav_sub, outputs=[
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
    ])
    '''bug here! '''

    class PrintUSNav:
        def run(self, ids, x, y, z, a, ts):
            print('[USNav] id:{} ({}, {}, {}) a:{}, ts:{}'.format(
                str(ids), str(x), str(y), str(z), str(a), str(ts)
            ))
    V.add(PrintUSNav(), inputs=[
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
    ])

    from parts.broker.sub import USNavRawSubscriber
    usnav_raw_sub = USNavRawSubscriber(factory, debug=True)
    V.add(usnav_raw_sub, outputs=[
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
    ])

    class PrintUSNavRaw:
        def run(self, ids, b1, b1d, b2, b2d, b3, b3d, b4, b4d, ts):
            print('[USNavRaw] id:{}, [{}]:{} [{}]:{} [{}]:{} [{}]:{} ts:{}'.format(
                str(ids), str(b1), str(b1d), str(b2), str(b2d), str(b3), str(b3d), str(b4), str(b4d), str(ts)
            ))
    V.add(PrintUSNavRaw(), inputs=[
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
    ])

    from parts.broker.sub import IMUSubscriber
    imu_sub = IMUSubscriber(factory, debug=True)
    V.add(imu_sub, outputs=[
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
    ])

    class PrintIMU:
        def run(self, x,y,z,qw,qx,qy,qz,vx,vy,vz,ax,ay,az,gx,gy,gz,mx,my,mz,ts):
            print('[IMU]({},{},{}) q({},{},{},{}) v({},{},{}) a({},{},{}) g({},{},{}) m({},{},{}) ts:{}'.format(
                str(x), str(y), str(z), str(qw), str(qx), str(qy), str(qz),
                str(vx), str(vy), str(vz), str(ax), str(ay), str(az),
                str(gx), str(gy), str(gz), str(mx), str(my), str(mz), str(ts)
            ))
    V.add(PrintIMU(), inputs=[
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
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
        sleep(5)


if __name__ == '__main__':
    test_sub()
