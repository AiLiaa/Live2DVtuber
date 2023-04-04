"""
其他面部特征检测实现
"""

import cv2
import numpy as np
from enum import Enum

class Eyes(Enum):
    LEFT = 1
    RIGHT = 2

class FacialFeatures:

    eye_key_indicies=[
        [
        # Left eye
        # 眼睛下轮廓
        33,
        7,
        163,
        144,
        145,
        153,
        154,
        155,
        133,
        # 眼睛上部轮廓（不包括角落）
        246,
        161,
        160,
        159,
        158,
        157,
        173
        ],
        [
        # Right eye
        # 眼睛下轮廓
        263,
        249,
        390,
        373,
        374,
        380,
        381,
        382,
        362,
        # 眼睛上部轮廓（不包括角落）
        466,
        388,
        387,
        386,
        385,
        384,
        398
        ]
    ]

    # 自定义img调整大小功能
    def resize_img(img, scale_percent):
        width = int(img.shape[1] * scale_percent / 100.0)
        height = int(img.shape[0] * scale_percent / 100.0)

        return cv2.resize(img, (width, height), interpolation = cv2.INTER_AREA)

    # 计算眼珠光比以检测闪烁
    # and/ or 控制眼睛的闭 / 开
    def eye_aspect_ratio(image_points, side):

        p1, p2, p3, p4, p5, p6 = 0, 0, 0, 0, 0, 0
        tip_of_eyebrow = 0

        # 首先获取img像素处的轮廓点
        # 遵循眼睛纵横比公式，稍作修改
        # 匹配facemesh模型
        #     2    3
        # 1            4
        #     6    5
        if side == Eyes.LEFT:

            eye_key_left = FacialFeatures.eye_key_indicies[0]

            p2 = np.true_divide(
                np.sum([image_points[eye_key_left[10]], image_points[eye_key_left[11]]], axis=0),
                2)
            p3 = np.true_divide(
                np.sum([image_points[eye_key_left[13]], image_points[eye_key_left[14]]], axis=0),
                2)
            p6 = np.true_divide(
                np.sum([image_points[eye_key_left[2]], image_points[eye_key_left[3]]], axis=0),
                2)
            p5 = np.true_divide(
                np.sum([image_points[eye_key_left[5]], image_points[eye_key_left[6]]], axis=0),
                2)
            p1 = image_points[eye_key_left[0]]
            p4 = image_points[eye_key_left[8]]

            tip_of_eyebrow = image_points[105]

        elif side == Eyes.RIGHT:
            eye_key_right = FacialFeatures.eye_key_indicies[1]

            p3 = np.true_divide(

                np.sum([image_points[eye_key_right[10]], image_points[eye_key_right[11]]], axis=0),
                2)
            p2 = np.true_divide(
                np.sum([image_points[eye_key_right[13]], image_points[eye_key_right[14]]], axis=0),
                2)
            p5 = np.true_divide(
                np.sum([image_points[eye_key_right[2]], image_points[eye_key_right[3]]], axis=0),
                2)
            p6 = np.true_divide(
                np.sum([image_points[eye_key_right[5]], image_points[eye_key_right[6]]], axis=0),
                2)
            p1 = image_points[eye_key_right[8]]
            p4 = image_points[eye_key_right[0]]

            tip_of_eyebrow = image_points[334]

        # EAR = （||p2-p6|| +||p3-p5||） ➗（ 2 * ||p1-p4||）
        ear = (np.linalg.norm(p2-p6) + np.linalg.norm(p3-p5))
        ear /= (2 * np.linalg.norm(p1-p4) + 1e-6)
        ear = ear * (np.linalg.norm(tip_of_eyebrow-image_points[2]) / np.linalg.norm(image_points[6]-image_points[2]))
        return ear

    # 计算口腔纵横比以检测口腔运动
    # 控制化身中嘴巴的打开/关闭
    def mouth_aspect_ratio(image_points):
        p1 = image_points[78]
        p2 = image_points[81]
        p3 = image_points[13]
        p4 = image_points[311]
        p5 = image_points[308]
        p6 = image_points[402]
        p7 = image_points[14]
        p8 = image_points[178]

        mar = np.linalg.norm(p2-p8) + np.linalg.norm(p3-p7) + np.linalg.norm(p4-p6)
        mar /= (2 * np.linalg.norm(p1-p5) + 1e-6)
        return mar

    def mouth_distance(image_points):
        p1 = image_points[78]
        p5 = image_points[308]
        return np.linalg.norm(p1-p5)


    # 通过mediapipe生成的新地标坐标检测虹膜
    # 替换旧的图像处理方法
    def detect_iris(image_points, iris_image_points, side):
        '''
            return:
                x_rate:虹膜向左的距离。0表示完全左侧，1表示完全右侧
                y_rate:虹膜向顶部的距离。0表示完全顶部，1表示完全底部
        '''

        iris_img_point = -1
        p1, p4 = 0, 0
        eye_y_high, eye_y_low = 0, 0
        x_rate, y_rate = 0.5, 0.5

        # 获取地标对应的图像坐标
        if side == Eyes.LEFT:
            iris_img_point = 468

            eye_key_left = FacialFeatures.eye_key_indicies[0]
            # 两眼角点
            p1 = image_points[eye_key_left[0]]
            p4 = image_points[eye_key_left[8]]

            eye_y_high = image_points[eye_key_left[12]]
            eye_y_low = image_points[eye_key_left[4]]

        elif side == Eyes.RIGHT:
            iris_img_point = 473

            eye_key_right = FacialFeatures.eye_key_indicies[1]
            p1 = image_points[eye_key_right[8]]
            p4 = image_points[eye_key_right[0]]

            eye_y_high = image_points[eye_key_right[12]]
            eye_y_low = image_points[eye_key_right[4]]

        p_iris = iris_image_points[iris_img_point - 468]

        # 求iris_image_point在p1和p4形成的直线上的投影
        # 通过矢量点积 得到 x_rate

        vec_p1_iris = [p_iris[0] - p1[0], p_iris[1] - p1[1]]
        vec_p1_p4 = [p4[0] - p1[0], p4[1] - p1[1]]
        
        x_rate = (np.dot(vec_p1_iris, vec_p1_p4) / (np.linalg.norm(p1-p4) + 1e-06)) / (np.linalg.norm(p1-p4) + 1e-06)

        #y-rate
        vec_eye_h_iris = [p_iris[0] - eye_y_high[0], p_iris[1] - eye_y_high[1]]
        vec_eye_h_eye_l = [eye_y_low[0] - eye_y_high[0], eye_y_low[1] - eye_y_high[1]]

        y_rate = (np.dot(vec_eye_h_eye_l, vec_eye_h_iris) / (np.linalg.norm(eye_y_high - eye_y_low) + 1e-06)) / (np.linalg.norm(eye_y_high - eye_y_low) + 1e-06)

        return x_rate, y_rate
