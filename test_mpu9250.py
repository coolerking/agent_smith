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
            'imu/recent', 'imu/mpu_timestamp'],
        threaded=False)

    try:
        V.start(rate_hz=20, max_loop_count=1000)
    except KeyboardInterrupt:
        pass
    finally:
        if pgio.connected:
            pgio.stop()


if __name__ == '__main__':
    test_mpu9250(use_debug=True)