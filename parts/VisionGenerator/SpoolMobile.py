# -*- coding: utf-8 -*-
"""
2D Map Pillwo(PIL) オブジェクトを取得するためのモジュールを提供する。
また Tkinter canvasオブジェクトを指定した場合は、canvasを更新する。
外部から利用する場合は、以下の情報が必要となる。
* ベースイメージファイル(JPEG)
* エージェントの座標(X, Y)および方向

外部モジュールから使用する場合は、 `SpoolMobileVision` クラスのみをcallすればよい。
"""
from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import math
# 摩擦抵抗値に対する指定色を定義した辞書
color_list = {0.001: '#E5E5E5', 0.3: '#00CB65', 0.002: '#00984C'}   # to be refactored


class MobileVision:
    """
    描画オブジェクトの抽象クラス。
    描画実装は円を描く処理となっている。
    """
    def __init__(self, id, x, y, angle, margin_x, margin_y, scale, landscape, canvas):
        """
        2D マップ上のオブジェクトの初期情報をインスタンス変数へ格納する。
        引数：
            id          Marvelmind モバイルビーコンID
            x           対象オブジェクトの開始時点のX座標
            y           対象オブジェクトの開始時点のY座標
            angle       画像左下を原点右をX軸、上をY軸としたときの角度(単位：度)
            margin_x    画像左下を原点としたときの上下X座標
            margin_y    画像左下を原点としたときの右左Y座標
            scale       画像をスケールアップする場合の倍率
            landscape   ベースイメージ(JPEG)
            canvas      Tkinterキャンバスオブジェクト
        戻り値：
            なし
        """

        # 移動体の識別id
        self.id = id
        # 箱庭座標系における位置とアングル
        self.position = np.zeros((2, 1))
        self.x = x  # 箱庭におけるスタート位置のX座標
        self.y = y  # 箱庭におけるスタート位置のY座標
        self.margin_x = margin_x    # Vision画像上での箱庭の左肩のX座標
        self.margin_y = margin_y    # Vision画像上での箱庭の左肩のX座標
        self.scale = scale  # 画像をスケールアップする場合の倍率
        self.position[0,0], self.position[1,0] = x, y   # 箱庭座標系における座標
        self.angle = angle  # 時計回りに0≦angle＜360
        self.landscape_img = landscape  # 箱庭とあみだ経路の書かれたJPEGイメージ
        self.w = canvas     # Canvasに表示する場合

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に半径self.scaleの円を描く。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # 回転中心の円とID
        mobile_radius = 2 * self.scale
        draw.ellipse((self.position[0, 0] * self.scale + self.margin_x - mobile_radius,
                      self.position[1, 0] * self.scale + self.margin_y - mobile_radius,
                      self.position[0, 0] * self.scale + self.margin_x + mobile_radius,
                      self.position[1, 0] * self.scale + self.margin_y + mobile_radius),
                     fill=(0, 255, 255), outline=(50, 50, 50))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に半径self.scaleの円を描く。
        引数：
            canvas      Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # 回転中心の円とID
        mobile_radius = 2 * self.scale
        canvas.delete(str(self.id) + "oval")
        canvas.create_oval(self.position[0, 0] * self.scale + self.margin_x - mobile_radius,
                           self.position[1, 0] * self.scale + self.margin_y - mobile_radius,
                           self.position[0, 0] * self.scale + self.margin_x + mobile_radius,
                           self.position[1, 0] * self.scale + self.margin_y + mobile_radius,
                           outline="#323232", fill="#00FFFF", tag=str(self.id) + "oval")


class Chassis(MobileVision):
    """
    エージェントのシャーシ描画オブジェクト。
    """
    # シャーシの座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 6))
    polygon[0, 0], polygon[1, 0] = 5.0, 2.5
    polygon[0, 1], polygon[1, 1] = 5.0, -13.03
    polygon[0, 2], polygon[1, 2] = 2.0, -15.03
    polygon[0, 3], polygon[1, 3] = -2.0, -15.03
    polygon[0, 4], polygon[1, 4] = -5.0, -13.03
    polygon[0, 5], polygon[1, 5] = -5.0, 2.5

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に6角形のポリゴン（シャーシ）を角度self.angle度傾けて描画する。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Chassis.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        draw.polygon(((rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y),
                      (rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y),
                      (rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y),
                      (rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y),
                      (rotated_polygon[0, 4] * self.scale + self.margin_x, rotated_polygon[1, 4] * self.scale + self.margin_y),
                      (rotated_polygon[0, 5] * self.scale + self.margin_x, rotated_polygon[1, 5] * self.scale + self.margin_y)),
                     fill=(255, 191, 0), outline=(76, 76, 76))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に6角形のポリゴン（シャーシ）を角度self.angle度傾けて描画する。
        引数：
            canvas  Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Chassis.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        canvas.delete(str(self.id) + "chassis")
        canvas.create_polygon(rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y,
                              rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y,
                              rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y,
                              rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y,
                              rotated_polygon[0, 4] * self.scale + self.margin_x, rotated_polygon[1, 4] * self.scale + self.margin_y,
                              rotated_polygon[0, 5] * self.scale + self.margin_x, rotated_polygon[1, 5] * self.scale + self.margin_y,
                              outline="#4C4C4C", fill="#E5E5E5", tag=str(self.id) + "chassis")


class Folk(MobileVision):
    """
    エージェントのフォーク部分描画オブジェクト。
    """
    # フォークの座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2,12))
    polygon[0, 0], polygon[1, 0] = -5.625, 3.5
    polygon[0, 1], polygon[1, 1] = -5.625, 3.875
    polygon[0, 2], polygon[1, 2] = -5.25, 3.875
    polygon[0, 3], polygon[1, 3] = -5.0, 11.25
    polygon[0, 4], polygon[1, 4] = -3.75, 11.25
    polygon[0, 5], polygon[1, 5] = -3.75, 3.875
    polygon[0, 6], polygon[1, 6] = 3.75, 3.875
    polygon[0, 7], polygon[1, 7] = 3.75, 11.25
    polygon[0, 8], polygon[1, 8] = 5.0, 11.25
    polygon[0, 9], polygon[1, 9] = 5.25, 3.875
    polygon[0, 10], polygon[1, 10] = 5.625, 3.875
    polygon[0, 11], polygon[1, 11] = 5.625, 3.5

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に12角形のポリゴン（フォーク）を角度self.angle度傾けて描画する。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_polygon = rot_matrix@Folk.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        draw.polygon(((rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y),
                      (rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y),
                      (rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y),
                      (rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y),
                      (rotated_polygon[0, 4] * self.scale + self.margin_x, rotated_polygon[1, 4] * self.scale + self.margin_y),
                      (rotated_polygon[0, 5] * self.scale + self.margin_x, rotated_polygon[1, 5] * self.scale + self.margin_y),
                      (rotated_polygon[0, 6] * self.scale + self.margin_x, rotated_polygon[1, 6] * self.scale + self.margin_y),
                      (rotated_polygon[0, 7] * self.scale + self.margin_x, rotated_polygon[1, 7] * self.scale + self.margin_y),
                      (rotated_polygon[0, 8] * self.scale + self.margin_x, rotated_polygon[1, 8] * self.scale + self.margin_y),
                      (rotated_polygon[0, 9] * self.scale + self.margin_x, rotated_polygon[1, 9] * self.scale + self.margin_y),
                      (rotated_polygon[0, 10] * self.scale + self.margin_x, rotated_polygon[1, 10] * self.scale + self.margin_y),
                      (rotated_polygon[0, 11] * self.scale + self.margin_x, rotated_polygon[1, 11] * self.scale + self.margin_y)),
                     fill=(204, 255, 255), outline=(76, 76, 76))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に12角形のポリゴン（フォーク）を角度self.angle度傾けて描画する。
        引数：
            canvas  Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_polygon = rot_matrix@Folk.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        canvas.delete(str(self.id) + "folk")
        canvas.create_polygon(rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y,
                              rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y,
                              rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y,
                              rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y,
                              rotated_polygon[0, 4] * self.scale + self.margin_x, rotated_polygon[1, 4] * self.scale + self.margin_y,
                              rotated_polygon[0, 5] * self.scale + self.margin_x, rotated_polygon[1, 5] * self.scale + self.margin_y,
                              rotated_polygon[0, 6] * self.scale + self.margin_x, rotated_polygon[1, 6] * self.scale + self.margin_y,
                              rotated_polygon[0, 7] * self.scale + self.margin_x, rotated_polygon[1, 7] * self.scale + self.margin_y,
                              rotated_polygon[0, 8] * self.scale + self.margin_x, rotated_polygon[1, 8] * self.scale + self.margin_y,
                              rotated_polygon[0, 9] * self.scale + self.margin_x, rotated_polygon[1, 9] * self.scale + self.margin_y,
                              rotated_polygon[0, 10] * self.scale + self.margin_x, rotated_polygon[1, 10] * self.scale + self.margin_y,
                              rotated_polygon[0, 11] * self.scale + self.margin_x, rotated_polygon[1, 11] * self.scale + self.margin_y,
                              outline="#4C4C4C", fill="#CCFFFF", tag=str(self.id) + "folk")


class Left_wheel(MobileVision):
    """
    左駆動輪描画オブジェクト。
    本体からの相対座標定義なので、各動輪ごとにオブジェクト定義している。
    """
    # 左駆動輪の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = 6.3125, 2.5
    polygon[0, 1], polygon[1, 1] = 4.3125, 2.5
    polygon[0, 2], polygon[1, 2] = 4.3125, -2.5
    polygon[0, 3], polygon[1, 3] = 6.3125, -2.5

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に4角形のポリゴン（左駆動輪）を角度self.angle度傾けて描画する。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Left_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        draw.polygon(((rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y),
                      (rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y),
                      (rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y),
                      (rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y)),
                     fill=(101, 101, 101), outline=(76, 76, 76))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に4角形のポリゴン（左駆動輪）を角度self.angle度傾けて描画する。
        引数：
            canvas  Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Left_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        canvas.delete(str(self.id) + "left_wheel")
        canvas.create_polygon(rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y,
                              rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y,
                              rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y,
                              rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y,
                              outline="#4C4C4C", fill="#656565", tag=str(self.id) + "left_wheel")


class Right_wheel(MobileVision):
    """
    右駆動輪描画オブジェクト。
    本体からの相対座標定義なので、各動輪ごとにオブジェクト定義している。
    """
    # 右駆動輪の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = -4.3125, 2.5
    polygon[0, 1], polygon[1, 1] = -6.3125, 2.5
    polygon[0, 2], polygon[1, 2] = -6.3125, -2.5
    polygon[0, 3], polygon[1, 3] = -4.3125, -2.5

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に4角形のポリゴン（右駆動輪）を角度self.angle度傾けて描画する。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Right_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        draw.polygon(((rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y),
                      (rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y),
                      (rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y),
                      (rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y)),
                     fill=(101, 101, 101), outline=(76, 76, 76))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に4角形のポリゴン（右駆動輪）を角度self.angle度傾けて描画する。
        引数：
            canvas  Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        # rotated_chassis = np.zeros((2, 4))
        rotated_polygon = rot_matrix@Right_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        canvas.delete(str(self.id) + "right_wheel")
        canvas.create_polygon(rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y,
                              rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y,
                              rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y,
                              rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y,
                              outline="#4C4C4C", fill="#656565", tag=str(self.id) + "right_wheel")


class Tail_wheel(MobileVision):
    """
    尾輪（非駆動）描画オブジェクト。
    本体からの相対座標定義なので、各動輪ごとにオブジェクト定義している。
    """
    # 尾輪（従動輪）の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = 1.0, -12.78
    polygon[0, 1], polygon[1, 1] = 1.0, -16.78
    polygon[0, 2], polygon[1, 2] = -1.0, -16.78
    polygon[0, 3], polygon[1, 3] = -1.0, -12.78

    def drawImage(self, draw):
        """
        Pillow(PIL)Drawオブジェクト上に4角形のポリゴン（尾輪）を角度self.angle度傾けて描画する。
        引数：
            draw    Pillow(PIL) Draw オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_polygon = rot_matrix@Tail_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        draw.polygon(((rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y),
                      (rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y),
                      (rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y),
                      (rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y)),
                     fill=(101, 101, 101), outline=(76, 76, 76))

    def drawCanvas(self, canvas):
        """
        Tkinter canvasオブジェクト上に4角形のポリゴン（尾輪）を角度self.angle度傾けて描画する。
        引数：
            canvas  Tkinter canvas オブジェクト  
        戻り値：
            なし
        """
        # -angleだけ回転する
        rot_matrix = [[math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))],
                      [-1 * math.sin(math.radians(self.angle)), math.cos(math.radians(self.angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_polygon = rot_matrix@Tail_wheel.polygon
        # self.position[]だけ平行移動
        rotated_polygon = rotated_polygon + self.position
        canvas.delete(str(self.id) + "tail_wheel")
        canvas.create_polygon(rotated_polygon[0, 0] * self.scale + self.margin_x, rotated_polygon[1, 0] * self.scale + self.margin_y,
                              rotated_polygon[0, 1] * self.scale + self.margin_x, rotated_polygon[1, 1] * self.scale + self.margin_y,
                              rotated_polygon[0, 2] * self.scale + self.margin_x, rotated_polygon[1, 2] * self.scale + self.margin_y,
                              rotated_polygon[0, 3] * self.scale + self.margin_x, rotated_polygon[1, 3] * self.scale + self.margin_y,
                              outline="#4C4C4C", fill="#656565", tag=str(self.id) + "tail_wheel")


class ResistanceMap:
    """
    摩擦抵抗データをもとにした2Dマップ Pillow(PIL) draw オブジェクトを
    生成するユーティリティクラス。
    """

    def __init__(self, inputMapFile, colorMapList):
        """
        摩擦抵抗ベースの2Dマップの初期情報をインスタンス変数へ格納する。
        引数：
            inputMapFile    ベースマップの摩擦抵抗データファイルへのパス
            colorMapFile    カラーマップファイル
                            （摩擦抵抗によって指定色を変更したデータが
                            格納されている）へのパス。本クラスでは使用されていない。
        戻り値：
            なし
        """
        self.inputMapFile = inputMapFile
        self.colorMapList = colorMapList

    def init_resistance_data(self):
        """
        摩擦抵抗データファイルを読み取り、カラーマップと突き合わせて
        摩擦抵抗データを作成・取得する。
        self.colorMapListは使用せず、決め打ちデータを作成、返却している。
        引数：
            なし
        戻り値：
            摩擦抵抗データ、
            (摩擦抵抗データファイル１行に含まれる要素数, 摩擦抵抗データファイル行数, 3)形式、
            各要素は色情報
        """
        f = open(self.inputMapFile)
        lines = f.readlines()
        datalen = len(lines)
        datanum = len(lines[0].split()) - 1
        f.close()
        data = np.zeros((datalen, datanum, 3))
        for j in range (datanum):
            for i in range (datalen):
                sp = lines[i].split()
                c = color_list.get(float(sp[j+1]))
                data[i, j, 0] = int(c[1:3], 16)
                data[i, j, 1] = int(c[3:5], 16)
                data[i, j, 2] = int(c[5:7], 16)
        return data

    def generateImageFile(self, outfilepath):
        """
        摩擦抵抗マップ画像を引数で指定されたパスへ保存し、Pillow(PIL) イメージを
        返却する。
        引数；
            outfilepath     摩擦抵抗マップ画像保存先ファイルパス
        戻り値：
            Pillow(PIL) イメージ（摩擦抵抗マップ画像）
        """
        resistance_list = ResistanceMap.init_resistance_data(self)
        pil_img = Image.fromarray(np.uint8(resistance_list))
        pil_img.save(outfilepath)
        return pil_img


class Landscape:
    """
    背景オブジェクト生成ユーティリティクラス。
    """
    def __init__(self, rrmap_img, weight_list, node_list, base_margin, ladder_margin, scale):
        """
        背景オブジェクトの初期情報をインスタンス変数へ格納する。
        引数：
            rrmap_img       摩擦抵抗カラーマップで彩色されたPillow(PIL)drawオブジェクト
            weight_list     重み付け境界座標のリスト
            node_list       エージェント（複数の可能性あり）座標のリスト
            base_margin     端からはしご状ガイドラインまでのマージン距離
            ladder_margin   はしご自体のマージン距離
            scale           画像化するさいの拡大・縮小率
        戻り値：
            なし
        """
        self.rrmap_img = rrmap_img # 走行抵抗イメージ
        self.weight_list = weight_list
        self.node_list = node_list
        self.base_margin = base_margin
        self.ladder_margin = ladder_margin
        self.scale = scale

    def create_1x1_landscape_img(self, margin_x, margin_y):
        """
        背景オブジェクトを作成し返却する。
        引数：
            margin_x        左右マージン距離
            margin_y        上下マージン距離
        戻り値：
            Pillow(PIL) 背景オブジェクト
        """
        if margin_x != 0 or margin_y != 0:
            result_img = Image.new(self.rrmap_img.mode, (self.rrmap_img.size[0] + margin_x * 2, self.rrmap_img.size[1] + margin_y * 2), (255, 255, 255))
            result_img.paste(self.rrmap_img, (margin_x, margin_y))
            self.rrmap_img = result_img

        if self.scale != 1:
            self.rrmap_img = self.rrmap_img.resize((self.rrmap_img.size[0] * self.scale, self.rrmap_img.size[1] * self.scale), Image.LANCZOS)

        draw = ImageDraw.Draw(self.rrmap_img)

        # draw nodes and legs on the resistance map
        node_circle_radius = 2 * self.scale
        display_offset_x = (margin_x + self.base_margin + self.ladder_margin) * self.scale
        display_offset_y = (margin_y + self.base_margin + self.ladder_margin) * self.scale

        node_list_d = []
        for i in range(len(self.node_list)):
            node_list_d.append([self.node_list[i, 0] * self.scale + display_offset_x, self.node_list[i, 1] * self.scale + display_offset_y])

        for j in range(len(self.weight_list)):
            for i in range(len(self.weight_list)):
                if self.weight_list[i, j] != 0:
                    draw.line(((node_list_d[i][0], node_list_d[i][1]), (node_list_d[j][0], node_list_d[j][1])),
                              fill=(0, 0, 203), width=1 * self.scale)

        for i in range(len(node_list_d)):
            draw.ellipse((node_list_d[i][0] - node_circle_radius, node_list_d[i][1] - node_circle_radius,
                          node_list_d[i][0] + node_circle_radius, node_list_d[i][1] + node_circle_radius),
                         fill=(0, 0, 203), outline=(0, 0, 203))

        return self.rrmap_img


class SpoolMobileVision(MobileVision):
    """
    2D Mapを作成するユーティリティクラス。
    """
    def __init__(self, id, x, y, angle, margin_x, margin_y, scale, landscape=None, canvas=None):
        """
        エージェント画像を構成する描画オブジェクトを生成し、Pillow(PIL) drawオブジェクトを更新する。
        Tkinter canvasオブジェクトを引数指定した場合は、canvasも更新する。
        引数：
            id          Marvelmind モバイルビーコンID
            x           対象オブジェクトの開始時点のX座標
            y           対象オブジェクトの開始時点のY座標
            angle       画像左下を原点右をX軸、上をY軸としたときの角度(単位：度)
            margin_x    画像左下を原点としたときの上下X座標
            margin_y    画像左下を原点としたときの右左Y座標
            scale       画像をスケールアップする場合の倍率
            landscape   ベースイメージ(JPEG)
            canvas      Tkinterキャンバスオブジェクト
        戻り値：
            なし
        """
        super().__init__(id, x, y, angle, margin_x, margin_y, scale, landscape, canvas)
        # self.landscape_img = landscape
        self.loader = [Folk(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas),
                       Chassis(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas),
                       MobileVision(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas),
                       Right_wheel(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas),
                       Left_wheel(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas),
                       Tail_wheel(self.id, self.x, self.y, self.angle, margin_x, margin_y, scale, landscape, canvas)]
        # paste the resistance map JPEG landscape image
        if canvas is not None:
            self.w = canvas
            # img = self.landscape_img.copy()
            # if self.scale != 1:
            #    self.landscape_img = self.landscape_img.resize((160 * self.scale, 120 * self.scale), Image.LANCZOS)
            #    self.landscape_img = ImageTk.PhotoImage(self.landscape_img)
            # self.w.create_image(0, 0, image=self.landscape_img, anchor=NW)
            for b in self.loader:
                b.position[0, 0], b.position[1, 0], b.angle = x, y, angle
                b.drawCanvas(self.w)

    def get_vision(self, x, y, angle):
        """
        最新の2D Map Pillow(PIL) draw オブジェクトを作成、返却する。
        引数：
            x           エージェントのX座標
            y           エージェントのY座標
            angle       エージェントの方向(単位：度、0から360)
        戻り値：
            vision      Pillow(PIL) drawオブジェクト（エージェント表示有2D Map）
        """
        vision = self.landscape_img.copy()
        for b in self.loader:
            b.position[0, 0], b.position[1, 0], b.angle = x, y, angle
            b.drawImage(ImageDraw.Draw(vision))
        return vision

    def update_vision(self, x, y, angle):
        """
        インスタンス変数self.canvasを最新の2D Map として更新する。
        引数：
            x           エージェントのX座標
            y           エージェントのY座標
            angle       エージェントの方向(単位：度、0から360)
        戻り値：
            なし
        """
        for b in self.loader:
            b.position[0, 0], b.position[1, 0], b.angle = x, y, angle
            b.drawCanvas(self.w)
