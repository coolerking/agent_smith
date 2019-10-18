# -*- coding: utf-8 -*-
"""
2D画像イメージを生成するパーツクラスを提供する。
要pillowパッケージ。
`pip install pillow`
"""
from PIL import Image
import numpy as np
import json

class MapImageCreator:
    """
    位置情報システムの出力データをもとにマップ画像を生成する
    パーツクラス。
    """
    def __init__(self, base_image_path, agent_image_path, another_agent_image_path, debug=False):
        """
        ベースイメージパス、エージェントイメージパスを
        インスタンス変数へ格納する。
        引数：
            base_image_path             ベースイメージパス
            agent_image_path            自エージェントイメージパス
            another_agent_image_path    他エージェントイメージパス
        """
        self.base_image_path = base_image_path
        self.agent_image_path = agent_image_path
        self.another_agent_image_path = another_agent_image_path
        self.debug = debug

    def run(self, x, y, z, qw, qx, qy, qz, hedge):
        """
        位置情報システムのX,Y,Z座標と四元数から
        マップ画像を生成し返却する。
        引数：
            x           位置情報システムX座標
            y           位置情報システムY座標
            z           位置情報システムZ座標
            qw          位置情報システム四元数w
            qx          位置情報システム四元数x
            qy          位置情報システム四元数y
            qz          位置情報システム四元数z
            hedge       ほかのエージェントの位置情報データ
        戻り値：
            image_array マップ画像
        """
        base_img = Image.open(self.base_image_path)
        if x is None or y is None or z is None or qw is None or qx is None or qy is None or qz is None:
            return np.array(base_img)
        elif x == 0 and y==0 and z==0:
            return np.array(base_img)
        agent_img = Image.open(self.agent_image_path)
        angle = self.quaternion_to_angle(qw, qx, qy, qz)
        agent_img.rotate(angle)
        base_x, base_y = self.convert_coordinates(x, y, z)
        base_img.paste(agent_img, (base_x, base_y))
        if self.debug:
            print('[MapImageCreator] my agent paste at ({}, {}) angle= {}'.format(
                str(base_x), str(base_y), str(angle)))
        
        # 他のエージェント情報を辞書化
        if hedge is None:
            hedge = '{}'
        hedge_dict = json.loads(hedge)

        # 他のエージェントイメージを追加
        for thing_name, tub_dict in hedge_dict.items():
            base_x, base_y, angle = self.get_position(tub_dict)
            another_agent_img = Image.open(self.agent_image_path)
            another_agent_img.rotate(angle)
            base_img.paste(another_agent_img, (base_x, base_y))
            if self.debug:
                print('[MapImageCreator] another agent {} paste at ({}, {}) angle= {}'.format(
                    thing_name, str(base_x), str(base_y), str(angle)))
        return np.array(base_img)

    def shutdown(self):
        """
        インスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.base_image_path = None
        self.agent_image_path = None

    def convert_coordinates(self, x, y, z):
        """
        位置情報システムのX,Y,Z座標をベースイメージ上の座標に変換する。
        引数：
            x       位置情報システムX座標
            y       位置情報システムY座標
            z       位置情報システムZ座標
        戻り値：
            base_x  ベースイメージ上のX座標
            base_y  ベースイメージ上のY座標
        """
        return x, y

    def quaternion_to_angle(self, qw, qx, qy, qz):
        """
        位置情報システムの四元数からベースイメージ上に
        配置するエージェント画像の回転角を決定する。
        引数：
            qw      位置情報システム四元数w
            qx      位置情報システム四元数x
            qy      位置情報システム四元数y
            qz      位置情報システム四元数z
        戻り値：
            base_x  ベースイメージ上のX座標
            base_y  ベースイメージ上のY座標
            angle   回転角
        """
        return 0

    def get_position(self, tub_dict):
        """
        Tubデータから必要な位置情報を取得する。
        引数：
            tub_dict    位置情報Tubデータ(辞書型)
        戻り値：
            angle   回転角
        """
        x = tub_dict.get('imu/x', 0)
        y = tub_dict.get('imu/y', 0)
        z = tub_dict.get('imu/z', 0)
        qw = tub_dict.get('imu/qw', 0)
        qx = tub_dict.get('imu/qx', 0)
        qy = tub_dict.get('imu/qy', 0)
        qz = tub_dict.get('imu/qz', 0)
        base_x, base_y = self.convert_coordinates(x, y, z)
        angle = self.quaternion_to_angle(qw, qx, qy, qz)
        return base_x, base_y, angle