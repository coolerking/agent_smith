from SpoolMobile import *
from ..sensors.marvelmind import MarvelmindHedge
from quaternion import Quaternion
from madgwickahrs import MadgwickAHRS
import math
import time
from tkinter import *
import numpy as np

global hedge
global heading
# global skip_very_first_data
# global dead_zone
# global angle
# global imu_processing_rate
# global x_end_ref  # Stationary beacon's position set as the end of x-axis by the dashboad randumly
# global origin_ref  # Stationary beacon's position set as the origin by the dashboad randumly

# angle = 0
skip_very_first_data = 0
dead_zone = 0.04 # lookes like we may consider the ombile beacon stationary in this range
imu_processing_rate = 143  # looks like 143~144msec is taken for proecssnig, don't know how to change
x_end_ref = np.zeros((2, 1))
origin_ref = np.zeros((2, 1))
x_end_ref[0, 0], x_end_ref[1, 0] = 76 * 0.008, 0  # cordinate of No.39 stationary beacon, as the x-axis end
origin_ref[0, 0], origin_ref[1, 0] = 0, 60 * 0.008  # cordiante of No.73 stationary beacon, as the origin

color_list = {0.001: '#E5E5E5', 0.3: '#00CB65', 0.002: '#00984C'}

start_node = 40
end_node = 1

debug = 0

dataname_weight = '1b1w.txt'
dataname_node = '1b1n.txt'
dataname_beacon = '1b1b.txt'

start_node_index = -1
end_node_index = -1

stud = 0.008

def init_weight_data(dataname):
    f = open(dataname)
    lines = f.readlines()
    datalen = len(lines)
    f.close()
    data = np.zeros((datalen, datalen))
    for j in range (datalen):
        for i in range (datalen):
            sp = lines[i].split()
            data[i,j] = sp[j+1]
    return data


def init_node_data(dataname):
    f = open(dataname)
    lines = f.readlines()
    datalen = len(lines)
    f.close()
    data = np.zeros((datalen, 2))
    for j in range (2):
        for i in range (datalen):
            sp = lines[i].split()
            data[i,j] = sp[j+1]
    return data


def init_beacon_data(dataname):
    f = open(dataname)
    lines = f.readlines()
    datalen = len(lines)
    f.close()
    data = np.zeros((datalen, 3))
    data0 = []
    for j in range (3):
        for i in range (datalen):
            sp = lines[i].split()
            if j==0:
                data0.append(sp[0])
            data[i,j] = sp[j+1]
    return data0, data


# 各Stationary beaconの座標情報
beacon_address, beacon_position = init_beacon_data(dataname_beacon)
print(beacon_address)
print(beacon_position)

# stationary beaconの座標系における箱庭座標系原点の座標 in studs
garden_axis = []
#garden_axis.append(830/8)
#garden_axis.append(770/8)
#garden_axis.append(-1*665/8)
garden_axis.append(0)
garden_axis.append(0)
garden_axis.append(-1*41)

if debug==1:
    print("箱庭座標系原点オフセット x:{:f} y:{:f} z:{:f}".format(garden_axis[0], garden_axis[1], garden_axis[2]))

# 各ノードの座標情報
node_list = init_node_data(dataname_node)
if debug==1:
    print(node_list)

# 各ノード間のコスト情報
weight_list = init_weight_data(dataname_weight)
# 始点/終点をweight_list(コストマトリクス)の両端列にスワップするためにオリジナルに影響しないコピーを作成
prop_route_list = np.copy(weight_list)

t0 = time.process_time()
node_num = len(prop_route_list) #ノードの数

master = Tk()

# Scale factor for viewing
scale = 4
margin_x = 1 * scale
margin_y = 1 * scale

# Ladder properties
ladder_aria_width = 128
ladder_aria_height = 96
leg_width = [16, 20, 28]

# base properties
# base_margin = 7
base_margin = 4
ladder_margin = 8
ladder_width = 16

# Ladder dimensions
ladder_x = ladder_aria_width * scale
ladder_y = ladder_aria_height * scale
leg_16 = leg_width[0] * scale
leg_20 = leg_width[1] * scale
leg_28 = leg_width[2] * scale

# roadway dimensions in studs
roadway_x = (ladder_aria_width + ladder_margin * 2) * scale
roadway_y = (ladder_aria_height + ladder_margin * 2) * scale

# base dimensions in studs
base_x = (ladder_aria_width + (ladder_margin + base_margin) * 2) * scale
base_y = (ladder_aria_height + (ladder_margin + base_margin) * 2) * scale

# base-of-shelf dimensions in studs
shelfBase_x = ladder_x - (ladder_width + ladder_margin) * 2 * scale
shelfBase_y = ladder_y - (ladder_width + ladder_margin) * 2 * scale

# shelf dimensions in studs
shelf_x = 20 * scale
shelf_y = 10 * scale
unit_x = 3
unit_y = 2

# Stationary beacon coordinates


# Course rendering here ---------------------------------------------------------------------------------
w = Canvas(master, width=base_x + margin_x * 2, height=base_y + margin_y * 2)
w.pack()

# base coodinates upper left 0 and lower_right 1
base_x0, base_y0 = margin_x, margin_y
base_x1, base_y1 = base_x0 + base_x, base_y0 + base_y
# base in green
w.create_rectangle(base_x0, base_y0, base_x1, base_y1, outline="#323232", fill="#6ed76e")

# roadway coodinates upper left 0 and lower_right 1
roadway_x0, roadway_y0 = base_x0 + base_margin * scale, base_y0 + base_margin * scale
roadway_x1, roadway_y1 = base_x1 - base_margin * scale, base_y1 - base_margin * scale
# roadway in gray
w.create_rectangle(roadway_x0, roadway_y0, roadway_x1, roadway_y1, outline="#323232", fill="#B2B2B2")

# shelf base coodinates upper left 0 and lower_right 1
shelfBase_x0, shelfBase_y0 = (base_x - shelfBase_x)/2 + margin_x, (base_y - shelfBase_y)/2 + margin_y
shelfBase_x1, shelfBase_y1 = shelfBase_x0 + shelfBase_x, shelfBase_y0 + shelfBase_y
# shelf base in green
w.create_rectangle(shelfBase_x0, shelfBase_y0, shelfBase_x1, shelfBase_y1, outline="#323232", fill="#6ed76e")

# shelf 3x2 layout
total_shelf_x, total_shelf_y = shelf_x * 3, shelf_y * 2
shelf_x0, shelf_y0 = (base_x - total_shelf_x)/2 + margin_x, (base_y - total_shelf_y)/2 + margin_y
shelf_x1, shelf_y1 = shelf_x0 + shelf_x, shelf_y0 + shelf_y
# shelf in blue
num_of_x = 0
shelf_x00 = shelf_x0
shelf_x11 = shelf_x1
while num_of_x < unit_x:
    num_of_y = 0
    shelf_y00 = shelf_y0
    shelf_y11 = shelf_y1
    while num_of_y < unit_y:
        w.create_rectangle(shelf_x00, shelf_y00, shelf_x11, shelf_y11, outline="#323232", fill="#00ffff")
        shelf_y00 = shelf_y00 + shelf_y
        shelf_y11 = shelf_y11 + shelf_y
        num_of_y = num_of_y + 1
    shelf_x00 = shelf_x00 + shelf_x
    shelf_x11 = shelf_x11 + shelf_x
    num_of_x = num_of_x + 1

node_circle_radius = 8
beacon_circle_radius = 8
display_offset_x = margin_x + (base_margin + ladder_margin) * scale
display_offset_y = margin_y + (base_margin + ladder_margin) * scale

node_list_d = []
for i in range(len(node_list)):
    node_list_d.append([node_list[i,0] * scale + display_offset_x, node_list[i,1] * scale + display_offset_y])

for j in range(len(weight_list)):
    for i in range(len(weight_list)):
        if weight_list[i,j] != 0:
            w.create_line(node_list_d[i], node_list_d[j], fill="yellow", width=3)
            if i < j:
                w.create_text((node_list_d[i][0] + node_list_d[j][0]) / 2,
                          (node_list_d[i][1] + node_list_d[j][1]) / 2 - node_circle_radius,
                          text="(%s,%s)" %(weight_list[i,j], weight_list[j,i]))
# nodes in yellow

for i in range(len(node_list_d)):
    w.create_oval(node_list_d[i][0] - node_circle_radius, node_list_d[i][1] - node_circle_radius, node_list_d[i][0] + node_circle_radius,node_list_d[i][1] + node_circle_radius, outline="#323232", fill="yellow")
    w.create_text(node_list_d[i][0], node_list_d[i][1], text=str(i+1))

# beacons in blue
beacon_list_d = []
for i in range(len(beacon_position)):
    beacon_list_d.append([beacon_position[i,0] * scale + margin_x, beacon_position[i,1] * scale + margin_y])
for i in range(len(beacon_list_d)):
    w.create_oval(beacon_list_d[i][0] - beacon_circle_radius, beacon_list_d[i][1] - beacon_circle_radius, beacon_list_d[i][0] + beacon_circle_radius, beacon_list_d[i][1] + beacon_circle_radius, outline="#323232", fill="#6ed76e")
    w.create_text(beacon_list_d[i][0], beacon_list_d[i][1], text=beacon_address[i])


def updateMiniatureWarehouseReferenceFrameData():
    global hedge
    global x_end_ref, origin_ref
    global angle
    global imu_processing_rate
    global skip_very_first_data
    global dead_zone

    # Miniature-Warehouse reference frame only concerns x, y position and yaw angle(around z-axis)
    # transform the Stationary-Beacon reference frame to the Miniature-Warehouse reference frame
    # Both stationary-beacon frame and the miniature-warehouse frame are rigth-hand-z-down reference.
    rotation_angle = math.degrees(math.atan2(origin_ref[1, 0], x_end_ref[0, 0]))
    position = np.zeros((2, 1))
    position[0, 0], position[1, 0] = hedge.valuesImuData[-1][0], hedge.valuesImuData[-1][1]

    # Rotete the processed position data (x, y) -1 * rotation_angle
    rot_matrix = [[math.cos(math.radians(rotation_angle)), math.sin(math.radians(rotation_angle))],
                  [-1 * math.sin(math.radians(rotation_angle)), math.cos(math.radians(rotation_angle))]]
    rot_matrix = np.array(rot_matrix)
    rotated_position = rot_matrix @ position

    # shift the rotatde position by origin_ref
    # print('rotated %f to p( %f, %f )' % (rotation_angle, rotated_position[0, 0], rotated_position[1,0]))
    rotated_position = rotated_position + origin_ref

    # transform the quaternian to the Euler angles (we need yaw angle only)
    # We use delta value to add the angle of mobile
    # while the absolute delta value is below 0.05 degree within the timeslice, we'll consider it as 0, that is stationary.
    q0, q1, q2, q3, timestamp = hedge.valuesImuData[-1][3], hedge.valuesImuData[-1][4], hedge.valuesImuData[-1][5], \
                                hedge.valuesImuData[-1][6], hedge.valuesImuData[-1][13]
    yaw = math.atan2(2.0 * (q1 * q2 + q0 * q3), q0 * q0 + q1 * q1 - q2 * q2 - q3 * q3)
    q10, q11, q12, q13, timestamp1 = hedge.valuesImuData[-2][3], hedge.valuesImuData[-2][4], hedge.valuesImuData[-2][5], \
                                     hedge.valuesImuData[-2][6], hedge.valuesImuData[-2][13]
    yaw1 = math.atan2(2.0 * (q11 * q12 + q10 * q13), q10 * q10 + q11 * q11 - q12 * q12 - q13 * q13)
    delta_yaw = math.degrees(yaw) - math.degrees(yaw1)
    elapsed_time = hedge.valuesImuData[-1][13] - hedge.valuesImuData[-2][13]

    if skip_very_first_data == 0:
        skip_very_first_data = 1
    else:
        if elapsed_time != 0:
            number_of_timeslice = elapsed_time / imu_processing_rate
            if abs(delta_yaw / number_of_timeslice) > dead_zone:
                angle = angle + delta_yaw
        else:
            if abs(delta_yaw) > dead_zone:
                angle = angle + delta_yaw

    # print('x:%f y:%f delta-yaw:%f angle:%f in %f msec sampled at %f msec' % (rotated_position[0, 0], rotated_position[1, 0], delta_yaw, angle % 360, elapsed_time, hedge.valuesImuData[-1][13]))
    dt_vision.update_vision(rotated_position[0, 0] / stud, rotated_position[1, 0] / stud, angle)


def updateImuMadgwickFilteredData():
    global hedge
    global heading
    global skip_very_first_data
    global dead_zone
    global angle
    delta_yaw = 0

    elapsed_time = hedge.valuesImuRawData[-1][9] - hedge.valuesImuRawData[-2][9]
    # heading.sampleperiod = elapsed_time / 1000
    gyr = np.array([math.radians(hedge.valuesImuRawData[-1][3]), math.radians(hedge.valuesImuRawData[-1][4]),
                    math.radians(hedge.valuesImuRawData[-1][5])])
    acc = np.array([hedge.valuesImuRawData[-1][0], hedge.valuesImuRawData[-1][1], hedge.valuesImuRawData[-1][2]])
    mgt = np.array([hedge.valuesImuRawData[-1][6], hedge.valuesImuRawData[-1][7], hedge.valuesImuRawData[-1][8]])
    heading.update(gyr, acc, mgt)
    roll, pitch, yaw = heading.quaternion.to_euler123()  # 最初の角度

    if skip_very_first_data != 0:  # 2回目以降は常に実行
        gyr1 = np.array([math.radians(hedge.valuesImuRawData[-2][3]), math.radians(hedge.valuesImuRawData[-2][4]),
                         math.radians(hedge.valuesImuRawData[-2][5])])
        acc1 = np.array([hedge.valuesImuRawData[-2][0], hedge.valuesImuRawData[-2][1], hedge.valuesImuRawData[-2][2]])
        mgt1 = np.array([hedge.valuesImuRawData[-2][6], hedge.valuesImuRawData[-2][7], hedge.valuesImuRawData[-2][8]])
        heading.update(gyr1, acc1, mgt1)
        roll1, pitch1, yaw1 = heading.quaternion.to_euler123()  # 最初の角度

    if skip_very_first_data == 0:
        angle = math.degrees(yaw)  # 方向を最初の角度に設定
        skip_very_first_data = 1
    else:
        delta_yaw = math.degrees(yaw) - math.degrees(yaw1)  # 2回目以降は差分を検査して加算する
        if elapsed_time != 0:
            number_of_timeslice = elapsed_time / imu_processing_rate
            if abs(delta_yaw / number_of_timeslice) > dead_zone:
                angle = angle + delta_yaw
        else:
            if abs(delta_yaw) > dead_zone:
                angle = angle + delta_yaw

    print('Turn %f degeres heading %f degrees elapsed time:%f' % (delta_yaw, angle % 360, elapsed_time))
    dt_vision.update_vision(76, 60, angle)

angle = 90
dt_vision = SpoolMobileVision(59, 76, 60, angle, 1 * scale, 1 * scale, scale, canvas=w)
# hedge = MarvelmindHedge(adr=59, tty="/dev/ttyACM0", baud=9600, maxvaluescount=32, recieveImuDataCallback=updateMiniatureWarehouseReferenceFrameData, debug=False)
hedge = MarvelmindHedge(adr=59, tty="/dev/ttyACM0", baud=38400, maxvaluescount=3, recieveImuRawDataCallback=updateImuMadgwickFilteredData, debug=False)
heading = MadgwickAHRS(sampleperiod=1/20, beta=2)
hedge.start()
mainloop()
