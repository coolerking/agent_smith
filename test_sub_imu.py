# -*- coding: utf-8 -*-
def test_sub_imu():
    
    try:
        import donkeycar as dk

    except:
        raise
    cfg = dk.load_config()
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import HedgeSubscriber, Mpu9250Subscriber
    h_sub = HedgeSubscriber(factory)
    V.add(h_sub, outputs=['hedge'])
    m_sub = Mpu9250Subscriber(factory)
    V.add(m_sub, outputs=['mpu9250'])

    class PrintMsg:
        def __init__(self, name):
            self.name = name
        def run(self, msg):
            print('[{}] msg={}'.format(self.name, str(msg)))
        def shutdown(self):
            pass

    V.add(PrintMsg('Hedge'), inputs=['hedge'])
    V.add(PrintMsg('Mpu9250'), inputs=['mpu9250'])

    try:
        V.start(rate_hz=20, max_loop_count=10000)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            factory.disconnect()
        except:
            print('ignore raise exception during aws factory disconnecting')


if __name__ == '__main__':
    test_sub_imu()