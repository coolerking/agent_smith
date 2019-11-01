# -*- coding: utf-8 -*-
from tkinter import *
from PIL import Image, ImageDraw
import numpy as np
import math
color_list = {0.001: '#E5E5E5', 0.3: '#00CB65', 0.002: '#00984C'}   # to be refactored


class MobileVision:
    def __init__(self, id, x, y, angle, margin_x, margin_y, scale, landscape, canvas):

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
        # 回転中心の円とID
        mobile_radius = 2 * self.scale
        draw.ellipse((self.position[0, 0] * self.scale + self.margin_x - mobile_radius,
                      self.position[1, 0] * self.scale + self.margin_y - mobile_radius,
                      self.position[0, 0] * self.scale + self.margin_x + mobile_radius,
                      self.position[1, 0] * self.scale + self.margin_y + mobile_radius),
                     fill=(0, 255, 255), outline=(50, 50, 50))

    def drawCanvas(self, canvas):
        # 回転中心の円とID
        mobile_radius = 2 * self.scale
        canvas.delete(str(self.id) + "oval")
        canvas.create_oval(self.position[0, 0] * self.scale + self.margin_x - mobile_radius,
                           self.position[1, 0] * self.scale + self.margin_y - mobile_radius,
                           self.position[0, 0] * self.scale + self.margin_x + mobile_radius,
                           self.position[1, 0] * self.scale + self.margin_y + mobile_radius,
                           outline="#323232", fill="#00FFFF", tag=str(self.id) + "oval")


class Chassis(MobileVision):
    # シャーシの座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 6))
    polygon[0, 0], polygon[1, 0] = 5.0, 2.5
    polygon[0, 1], polygon[1, 1] = 5.0, -13.03
    polygon[0, 2], polygon[1, 2] = 2.0, -15.03
    polygon[0, 3], polygon[1, 3] = -2.0, -15.03
    polygon[0, 4], polygon[1, 4] = -5.0, -13.03
    polygon[0, 5], polygon[1, 5] = -5.0, 2.5

    def drawImage(self, draw):
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
    # 左駆動輪の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = 6.3125, 2.5
    polygon[0, 1], polygon[1, 1] = 4.3125, 2.5
    polygon[0, 2], polygon[1, 2] = 4.3125, -2.5
    polygon[0, 3], polygon[1, 3] = 6.3125, -2.5

    def drawImage(self, draw):
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
    # 右駆動輪の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = -4.3125, 2.5
    polygon[0, 1], polygon[1, 1] = -6.3125, 2.5
    polygon[0, 2], polygon[1, 2] = -6.3125, -2.5
    polygon[0, 3], polygon[1, 3] = -4.3125, -2.5

    def drawImage(self, draw):
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
    # 尾輪（従動輪）の座標。箱庭座標系においてangle0度のときの重心（self.position[]）を原点とする座標
    polygon = np.zeros((2, 4))
    polygon[0, 0], polygon[1, 0] = 1.0, -12.78
    polygon[0, 1], polygon[1, 1] = 1.0, -16.78
    polygon[0, 2], polygon[1, 2] = -1.0, -16.78
    polygon[0, 3], polygon[1, 3] = -1.0, -12.78

    def drawImage(self, draw):
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

    def __init__(self, inputMapFile, colorMapList):
        self.inputMapFile = inputMapFile
        self.colorMapList = colorMapList

    def init_resistance_data(self):
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
        resistance_list = ResistanceMap.init_resistance_data(self)
        pil_img = Image.fromarray(np.uint8(resistance_list))
        pil_img.save(outfilepath)
        return pil_img


class Landscape:
    def __init__(self, rrmap_img, weight_list, node_list, base_margin, ladder_margin, scale):
        self.rrmap_img = rrmap_img # 走行抵抗イメージ
        self.weight_list = weight_list
        self.node_list = node_list
        self.base_margin = base_margin
        self.ladder_margin = ladder_margin
        self.scale = scale

    def create_1x1_landscape_img(self, margin_x, margin_y):
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
    def __init__(self, id, x, y, angle, margin_x, margin_y, scale, landscape=None, canvas=None):
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
        vision = self.landscape_img.copy()
        for b in self.loader:
            b.position[0, 0], b.position[1, 0], b.angle = x, y, angle
            b.drawImage(ImageDraw.Draw(vision))
        return vision

    def update_vision(self, x, y, angle):
        for b in self.loader:
            b.position[0, 0], b.position[1, 0], b.angle = x, y, angle
            b.drawCanvas(self.w)



