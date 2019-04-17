# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
オートパイロットKerasLinearのトレーニングを実行し、モデルファイルを作成する。

Usage:
    train.py [--tub=<tub1,tub2,..tubn>]  [--model=<model>] [--base_model=<base_model>]

Options:
    -h --help                   ヘルプを表示する
    --tub TUBPATHS              タブディレクトリパスを指定する
    --model MODELPATH           出力モデルファイルのパスを指定する
    --base_model BASEMODELPATH  初期状態のモデルをモデルファイルからロードする場合、ファイルパスを指定する
"""
import os

from docopt import docopt
import donkeycar as dk
from donkeycar.parts.datastore import TubGroup
from pilot.keras import KerasLinear
from copus import agent_record_transform



def train(cfg, tub_names, new_model_path, base_model_path=None):
    """
    use the specified data in tub_names to train an artifical neural network
    saves the output trained model as model_name
    """
    X_keys = ['cam/image_array']
    y_keys = ['user/left/value', 'user/left/status', 'user/right/value', 'user/right/status', 
    'user/lift/value', 'user/lift/status']

    new_model_path = os.path.expanduser(new_model_path)

    kl = KerasLinear()
    if base_model_path is not None:
        base_model_path = os.path.expanduser(base_model_path)
        kl.load(base_model_path)

    print('tub_names', tub_names)
    if not tub_names:
        tub_names = os.path.join(cfg.DATA_PATH, '*')
    tubgroup = TubGroup(tub_names)
    train_gen, val_gen = tubgroup.get_train_val_gen(X_keys, y_keys,
                                                    batch_size=cfg.BATCH_SIZE,
                                                    train_frac=cfg.TRAIN_TEST_SPLIT,
                                                    train_record_transform=agent_record_transform,
                                                    val_record_transform=agent_record_transform)

    total_records = len(tubgroup.df)
    total_train = int(total_records * cfg.TRAIN_TEST_SPLIT)
    total_val = total_records - total_train
    print('train: %d, validation: %d' % (total_train, total_val))
    steps_per_epoch = total_train // cfg.BATCH_SIZE
    print('steps_per_epoch', steps_per_epoch)

    kl.train(train_gen,
             val_gen,
             saved_model_path=new_model_path,
             steps=steps_per_epoch,
             train_split=cfg.TRAIN_TEST_SPLIT)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()


    tub = args.get('--tub', 'tub')
    new_model_path = args.get('--model', os.path.join('models', 'pilot'))
    base_model_path = args['--base_model']
    cache = not args['--no_cache']
    train(cfg, tub, new_model_path, base_model_path)





