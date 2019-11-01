# -*- coding: utf-8 -*-
from SpoolMobile import *
from marvelmind import MarvelmindHedge
from PIL import *
import numpy as np


angle = 90  # x-axis +direction

dead_zone = 0.05  # looks like we may consider the mobile beacon stationary in this range
imu_processing_rate = 143  # looks like 143~144 msec is taken for processing, don't know how to change
x_end_ref = np.zeros((2,1))  # Stationary beacon's position set as the end of x-axis by the dashboard randomly
origin_ref = np.zeros((2,1))  # Stationary beacon's position set as the origin by the dashboard random
x_end_ref[0,0], x_end_ref[1,0] = 76 * 0.008, 0  # coordinate of No.39 stationary beacon, as the x-axis end
origin_ref[0,0], origin_ref[1,0] = 0, 60 * 0.008  # coordinate of No.73 stationary beacon, as the origin
landscape_file_path = '1x1_landscape.jpg'   # warehouse and ladder image file
file_name_trailer_count = 0
skip_very_first_data = 0
scale = 1   # always 1 for vision generation
stud = 8 / 1000     # 8mm/stud

debug = 0

def updateMiniatureWarehouseReferenceFrameData():
    global hedge
    global x_end_ref, origin_ref
    global angle
    global imu_processing_rate
    global skip_very_first_data
    global dead_zone
    global file_name_trailer_count
    global dt_vision

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
    q0, q1, q2, q3, timestamp = hedge.valuesImuData[-1][3], hedge.valuesImuData[-1][4], hedge.valuesImuData[-1][5], hedge.valuesImuData[-1][6], hedge.valuesImuData[-1][13]
    yaw = math.atan2(2.0 * (q1 * q2 + q0 * q3), q0 * q0 + q1 * q1 - q2 * q2 - q3 * q3)
    q10, q11, q12, q13, timestamp1 = hedge.valuesImuData[-2][3], hedge.valuesImuData[-2][4], hedge.valuesImuData[-2][5], hedge.valuesImuData[-2][6], hedge.valuesImuData[-2][13]
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

    if debug == 1:
        print('x:%f y:%f delta-yaw:%f angle:%f in %f msec sampled at %f msec' % (rotated_position[0, 0], rotated_position[1, 0], delta_yaw, angle % 360, elapsed_time, hedge.valuesImuData[-1][13]))
    im = dt_vision.get_vision(rotated_position[0, 0] / stud, rotated_position[1, 0] / stud, angle)
    
    # 以下はチェクのため
    if debug == 1:
        test_img_file_path = './out_box/img' + str(file_name_trailer_count + 1) + '.jpg'
        file_name_trailer_count = file_name_trailer_count + 1
        im.save(test_img_file_path, quality=95)
    

def main():
    global hedge
    global dt_vision    # ローカルに配置しておいた俯瞰図landscapeを視野画像の風景としてオンメモリーにロードしておくため
    global angle
    #  X=20, y=20, angle=90の設定では
    #  Loaderの初期位置は原点（#73と#39ビーコンの間の角）に対して（20ポチ,20ポチ)=(0.16m, 0.16m)のところで#39ビーコンの方角を向いている
    dt_vision = SpoolMobileVision(59, 20, 20, angle, 4, 0, scale, landscape=Image.open(landscape_file_path))
    hedge = MarvelmindHedge(adr=59, tty="/dev/ttyACM0", baud=38400, maxvaluescount=12, recieveImuDataCallback=updateMiniatureWarehouseReferenceFrameData, debug=False)
    hedge.start()
    while True:
        try:
            pass  # time.sleep(0.020)
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port
            sys.exit()


if __name__ == "__main__":
    main()



