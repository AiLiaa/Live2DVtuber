"""
根据面部标志点估计头部姿势
"""
import cv2
import numpy as np
import config

class PoseEstimator:

    def __init__(self, img_size=(480, 640)):
        self.size = img_size

        self.model_points_full = self.get_full_model_points()

        # 摄像机内部
        self.focal_length = self.size[1]
        self.camera_center = (self.size[1] / 2, self.size[0] / 2)
        self.camera_matrix = np.array(
            # 内参矩阵：
            # 焦距f和光学中心c
            [[self.focal_length, 0, self.camera_center[0]],
             [0, self.focal_length, self.camera_center[1]],
             [0, 0, 1]], dtype="double")

        # 假设没有透镜畸变
        self.dist_coeefs = np.zeros((4, 1))

        # 旋转矢量和平移矢量
        self.r_vec = None
        self.t_vec = None

    def get_full_model_points(self, filename='config/model.txt'):
        """从文件中获取所有468个三维模型点"""
        raw_value = []

        with open(filename) as file:
            for line in file:
                raw_value.append(line)

        model_points = np.array(raw_value, dtype=np.float32)
        model_points = np.reshape(model_points, (-1, 3))

        return model_points

    def solve_pose_by_all_points(self, image_points):
        """
        从所有468个图像点求解位姿
        返回（旋转矢量，平移矢量）作为位姿。
        """

        if self.r_vec is None:
            # 通过世界中的N个特征点与图像成像中的N个像点，计算出其投影关系，从而获得相机或物体位姿
            (_, rotation_vector, translation_vector) = cv2.solvePnP(
                # 世界坐标系下参考点的3D坐标系
                # 3D坐标对应相机图像坐标系上的2D投影点
                # 相机的内参矩阵
                # 相机畸变系数
                self.model_points_full, image_points, self.camera_matrix, self.dist_coeefs)
            self.r_vec = rotation_vector
            self.t_vec = translation_vector

        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            self.model_points_full,
            image_points,
            self.camera_matrix,
            self.dist_coeefs,
            rvec=self.r_vec,
            tvec=self.t_vec,
            # 用于SOLVEPNP迭代的参数，函数使用提供的rvec和tvec值分别作为旋转和平移向量的初始近似，并进一步优化它们
            useExtrinsicGuess=True)
        return (rotation_vector, translation_vector)

    def draw_annotation_box(self, image, rotation_vector, translation_vector, color=(255, 255, 255), line_width=2):
        """
        绘制三维长方体作为姿势的注释
        """
        point_3d = []
        rear_size = 75
        rear_depth = 0
        point_3d.append((-rear_size, -rear_size, rear_depth))
        point_3d.append((-rear_size, rear_size, rear_depth))
        point_3d.append((rear_size, rear_size, rear_depth))
        point_3d.append((rear_size, -rear_size, rear_depth))
        point_3d.append((-rear_size, -rear_size, rear_depth))

        front_size = 40
        front_depth = 400
        point_3d.append((-front_size, -front_size, front_depth))
        point_3d.append((-front_size, front_size, front_depth))
        point_3d.append((front_size, front_size, front_depth))
        point_3d.append((front_size, -front_size, front_depth))
        point_3d.append((-front_size, -front_size, front_depth))
        point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)

        # 映射到2d图像点
        (point_2d, _) = cv2.projectPoints(point_3d,
                                          rotation_vector,
                                          translation_vector,
                                          self.camera_matrix,
                                          self.dist_coeefs)
        point_2d = np.int32(point_2d.reshape(-1, 2))

        # 画所有的线
        cv2.polylines(image, [point_2d], True, color, line_width, cv2.LINE_AA)
        cv2.line(image, tuple(point_2d[1]), tuple(
            point_2d[6]), color, line_width, cv2.LINE_AA)
        cv2.line(image, tuple(point_2d[2]), tuple(
            point_2d[7]), color, line_width, cv2.LINE_AA)
        cv2.line(image, tuple(point_2d[3]), tuple(
            point_2d[8]), color, line_width, cv2.LINE_AA)


    def draw_axis(self, img, R, t):
        axis_length = 20
        axis = np.float32(
            [[axis_length, 0, 0], [0, axis_length, 0], [0, 0, axis_length]]).reshape(-1, 3)

        axisPoints, _ = cv2.projectPoints(
            axis, R, t, self.camera_matrix, self.dist_coeefs)

        img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
            axisPoints[0].ravel()), (255, 0, 0), 3)
        img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
            axisPoints[1].ravel()), (0, 255, 0), 3)
        img = cv2.line(img, tuple(axisPoints[3].ravel()), tuple(
            axisPoints[2].ravel()), (0, 0, 255), 3)

    def draw_axes(self, img, R, t):
            img	= cv2.drawFrameAxes(img, self.camera_matrix, self.dist_coeefs, R, t, 20)

    def reset_r_vec_t_vec(self):
        self.r_vec = None
        self.t_vec = None
