# -*- coding: utf-8 -*-


def test_mpu9250(use_debug=False):
    import donkeycar as dk
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    try:
        import pigpio
    except:
        raise
    pgio = pigpio.pi()

    from parts.sensors.imu import Mpu9250
    imu = Mpu9250(
        pgio=pgio,
        bus=cfg.MPC9250_I2C_BUS, 
        mpu9250_address=cfg.M9250_I2C_ADDRESS, 
        ak8963_address=cfg.AK8963_I2C_ADDRESS, 
        debug=use_debug)
    V.add(imu,
        outputs=[
            'imu/ax', 'imu/ay', 'imu/az',
            'imu/gx', 'imu/gy', 'imu/gz', 
            'imu/mx', 'imu/my', 'imu/mz', 'imu/temp',
            'imu/timestamp'],
        threaded=True)

    class PrintIMU:
        def run(self, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, mgt_x, mgt_y, mgt_z, temp, timestamp):
            print('acc:({}, {}, {}) gyr:({}, {}, {}) mgt:({}, {}, {}) temp:{}, ts:{}'.format(
                str(acc_x), str(acc_y), str(acc_z), str(gyr_x), str(gyr_y), str(gyr_z), 
                str(mgt_x), str(mgt_y), str(mgt_z), str(temp), str(timestamp)
            ))
    V.add(PrintIMU(), inputs=[
        'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 
        'imu/mx', 'imu/my', 'imu/mz', 'imu/temp',
        'imu/timestamp'
    ])

    try:
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, 
                max_loop_count=cfg.MAX_LOOPS)
    except KeyboardInterrupt:
        pass
    finally:
        V.stop()
        pgio.stop()


if __name__ == '__main__':
    test_mpu9250(use_debug=True)