import math


class BodyFeatures:
    body_key_indicies=[
        # 右手
        [
            24,
            12,
            14,
            16,
            20
        ],
        # 左手
        [
            23,
            11,
            13,
            15,
            19
        ],
        # yao
        [
            12,
            24,
            26,
            11,
            23,
            25
        ],
        # 右腿
        [
            23,
            24,
            26,
            28,
            32
        ],
        # 左腿
        [
            24,
            23,
            25,
            27,
            31
        ]
    ]
    # 获取肢体角度
    def findAngle(self, image_points, p1, p2, p3):
        # 获取标记点
        x1, y1 = image_points[p1]
        x2, y2 = image_points[p2]
        x3, y3 = image_points[p3]
        # 计算
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        return round(angle, 4)

    def findAllAngle(self, image_points):
        angles = []

        right_shoulder_angle = self.findAngle(image_points, 24, 12, 14)
        right_elbow_angle = self.findAngle(image_points, 12, 14, 16)
        right_wrist_angle = self.findAngle(image_points, 20, 16, 14)
        left_shoulder_angle = self.findAngle(image_points, 13, 11, 23)
        left_elbow_angle = self.findAngle(image_points, 15, 13, 11)
        left_wrist_angle = self.findAngle(image_points, 19, 15, 13)

        right_shoulder_inner_angle = self.findAngle(image_points, 11, 12, 24)
        right_hip_angle = self.findAngle(image_points, 26, 24, 12)
        left_shoulder_inner_angle = self.findAngle(image_points, 23, 11, 12)
        left_hip_angle = self.findAngle(image_points, 11, 23, 25)

        right_leg_angle = self.findAngle(image_points, 23, 24, 26)
        right_knee_angle = self.findAngle(image_points, 24, 26, 28)
        right_ankle_angle = self.findAngle(image_points, 26, 28, 32)
        left_leg_angle = self.findAngle(image_points, 25, 23, 24)
        left_knee_angle = self.findAngle(image_points, 27, 25, 23)
        left_ankle_angle = self.findAngle(image_points, 31, 27, 25)

        angles.append(right_shoulder_angle)
        angles.append(right_elbow_angle)
        angles.append(right_wrist_angle)
        angles.append(left_shoulder_angle)
        angles.append(left_elbow_angle)
        angles.append(left_wrist_angle)

        angles.append(right_shoulder_inner_angle)
        angles.append(right_hip_angle)
        angles.append(left_shoulder_inner_angle)
        angles.append(left_hip_angle)

        angles.append(right_leg_angle)
        angles.append(right_knee_angle)
        angles.append(right_ankle_angle)
        angles.append(left_leg_angle)
        angles.append(left_knee_angle)
        angles.append(left_ankle_angle)

        return angles