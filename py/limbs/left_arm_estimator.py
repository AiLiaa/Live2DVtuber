import cv2
import numpy as np
import config
class LeftArmPoseEstimator:

    def __init__(self, img_size=(480, 640)):
        self.size = img_size

        self.left_arm_model_points_full = self.get_full_left_arm_model_points()

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

    def get_full_left_arm_model_points(self, filename='config/model_left_arm.txt'):
        raw_value = []

        with open(filename) as file:
            for line in file:
                raw_value.append(line)

        model_points = np.array(raw_value, dtype=np.float32)
        model_points = np.reshape(model_points, (-1, 3))

        return model_points

    def solve_left_arm_pose_by_all_points(self, image_points):
        """
        从所有图像点求解位姿
        返回（旋转矢量，平移矢量）作为位姿。
        """

        if self.r_vec is None:
            # 通过世界中的N个特征点与图像成像中的N个像点，计算出其投影关系，从而获得相机或物体位姿
            (_, rotation_vector, translation_vector) = cv2.solvePnP(
                # 世界坐标系下参考点的3D坐标系
                # 3D坐标对应相机图像坐标系上的2D投影点
                # 相机的内参矩阵
                # 相机畸变系数
                self.left_arm_model_points_full, image_points, self.camera_matrix, self.dist_coeefs)
            self.r_vec = rotation_vector
            self.t_vec = translation_vector

        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            self.left_arm_model_points_full,
            image_points,
            self.camera_matrix,
            self.dist_coeefs,
            rvec=self.r_vec,
            tvec=self.t_vec,
            # 用于SOLVEPNP迭代的参数，函数使用提供的rvec和tvec值分别作为旋转和平移向量的初始近似，并进一步优化它们
            useExtrinsicGuess=True)
        return (rotation_vector, translation_vector)
