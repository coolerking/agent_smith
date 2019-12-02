# -*- coding: utf-8 -*-
"""
Tubディレクトリ上のデータをAWS IoT Coreへ送信する。

Usage:
    tub_player.py [--aws_conf <aws config yaml path>] [--aws_target <aws target name>] [--tub=<tub dir path>] [--auto_repeat]

Options:
    --tub <tub_dir_path>                タブディレクトリ(ex. data/tub_9_99-99-99)
    --aws_conf <aws config yaml path>   AWS IoT Core設定ファイルパス
    --aws_target <aws target name>      AWS IoT Core設定ファイル内のターゲット名
    --auto_repeat                       無限に繰り返す
"""
import time
try:
    from docopt import docopt
except ImportError:
    exit('This code requires docopt package.')
try:
    import donkeycar as dk
except ImportError:
    exit('This code requires donkeycar package.')

def play(cfg, tub_dir, aws_conf, aws_target, repeat):
    V = dk.vehicle.Vehicle()



    from parts.loader import UserLoader, ImageLoader
    user_loader = UserLoader(tub_dir, repeat=repeat)
    V.add(user_loader, outputs=[
        'user/mode',
        'user/angle',
        'user/throttle',
        'user/lift_throttle',
        'timestamp',
    ])
    image_loader = ImageLoader(tub_dir, repeat=repeat)
    V.add(image_loader, outputs=[
        'cam/image_array',
    ])

    if aws_conf and aws_target:
        from parts.broker import AWSShadowClientFactory
        factory = AWSShadowClientFactory(aws_conf, aws_target)

        from parts.broker import PowerReporter
        power = PowerReporter(factory, debug=False)
        print('[tub_player] power on {}'.format(str(aws_target)))
        power.on()
        
        from parts.broker.pub import UserPublisher
        user_pub = UserPublisher(factory, debug=False)
        V.add(user_pub, inputs=[
            'user/angle',
            'user/throttle',
            'user/lift_throttle',
            'user/mode',
        ])
    else:
        print('debug mode: no publishing')
    class PrintTub:
        def run(self, user_angle, user_throttle, user_lift_throttle, user_mode):
            print('[tub_player] mode:{} angle:{} throttle:{}, lift:{}'.format(
                str(user_mode),
                str(user_angle),
                str(user_throttle),
                str(user_lift_throttle),
            ))
    prt = PrintTub()
    V.add(prt, inputs=[
        'user/angle',
        'user/throttle',
        'user/lift_throttle',
        'user/mode',
    ])

    try:
        print('[tub_player] start running')
        #run the vehicle for 20 seconds
        max_loop_count = None if repeat else cfg.MAX_LOOPS
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, 
                max_loop_count=max_loop_count)
    except KeyboardInterrupt:
        # Ctrl+C押下時
        pass
    finally:
        if aws_conf and aws_target:
            power.off()
            print('[tub_player] power off {}'.format(str(aws_target)))
            try:
                factory.disconnect()
            except TimeoutError:
                print('aws disconnect timeout')
            except:
                raise
        print('[tub_player] Stopped')

if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    tub_dir = args.get('--tub', cfg.DATA_PATH)
    aws_conf = args['--aws_conf']
    aws_target = args['--aws_target']
    repeat = args['--auto_repeat']

    play(cfg, tub_dir, aws_conf, aws_target, repeat)
