# -*- coding: utf-8 -*-

from time import time

def test_sub(use_debug=False):
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory, PowerReporter
    factory = AWSShadowClientFactory('conf/aws/tom.yml', 'tom')
    # Power ON 情報の送信
    power = PowerReporter(factory, debug=use_debug)
    power.on()

    from parts.broker import HedgeSubscriber
    sub = HedgeSubscriber(factory, debug=use_debug)
    V.add(sub, outputs=['hedge'])

    class PrintHedge:
        def run(self, hedge):
            print(hedge)
        def shutdown(self):
            pass

    prt = PrintHedge()
    V.add(prt, inputs=['hedge'])

    V.mem['hedge'] = 'yet subscribed'

    try:
        print('Start running')
        #run the vehicle for 20 seconds
        V.start(rate_hz=20, 
                max_loop_count=10000)
    except KeyboardInterrupt:
        # Ctrl+C押下時
        pass
    finally:
        # デバッグ
        if use_debug:
            print('Stop running')
        if power is not None:
            if use_debug:
                print('Sending power off')
            power.off()
            power = None
        if factory is not None:
            if use_debug:
                print('Disconnecting aws iot')
            factory.disconnect()
            factory = None
        print('Stopped')


if __name__ == '__main__':
    test_sub(use_debug=True)