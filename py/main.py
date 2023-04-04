"""
主程序运行检测和TCP
"""

from argparse import ArgumentParser
import cv2
import numpy as np


import socket

from face.facial_landmark import FaceMeshDetector

from body.body_landmark import BodyPoseDetector


from face.pose_estimator import PoseEstimator
from body.bodypose_estimator import BodyPoseEstimator
from limbs.left_arm_estimator import LeftArmPoseEstimator
from utils.stabilizer import Stabilizer

from face.facial_features import FacialFeatures, Eyes

from body.body_features import BodyFeatures

import sys


# 端口号
port = 5066

# init TCP connection with unity
def init_TCP():
    port = args.port

    address = ('127.0.0.1', port)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)

        print("Connected to address:", socket.gethostbyname(socket.gethostname()) + ":" + str(port))
        return s
    except OSError as e:
        print("Error while connecting :: %s" % e)
        
        # 如果连接失败，退出脚本（例如Unity server端突然退出）
        sys.exit()


def send_info_to_unity(s, args):
    msg = '%.4f ' * len(args) % args

    try:
        s.send(bytes(msg, "utf-8"))
    except socket.error as e:
        print("error while sending :: " + str(e))

        sys.exit()

def print_debug_msg(args):
    msg = '%.4f ' * len(args) % args
    print(msg)

def main():


    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Facemesh
    detector = FaceMeshDetector()
    # Body
    bodyDector = BodyPoseDetector()

    # 获取位姿估计img的样本帧
    success, img = cap.read()

    # 与位姿估计相关
    pose_estimator = PoseEstimator((img.shape[0], img.shape[1]))
    image_points = np.zeros((pose_estimator.model_points_full.shape[0], 2))

    body_pose_estimator = BodyPoseEstimator((img.shape[0], img.shape[1]))
    body_image_points = np.zeros((body_pose_estimator.body_model_points_full.shape[0], 2))

    left_arm_pose_estimator = LeftArmPoseEstimator((img.shape[0], img.shape[1]))
    letf_arm_image = np.zeros((left_arm_pose_estimator.left_arm_model_points_full.shape[0], 2))

    # 由于新的模型（虹膜检测中），额外10点
    iris_image_points = np.zeros((10, 2))

    # 引入标量稳定器
    # for pose
    pose_stabilizers = [Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    # for left arm pose
    left_arm_pose_stabilizers = [Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    # for body pose
    body_pose_stabilizers = [Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    # for eyes
    eyes_stabilizers = [Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    # for mouth_dist
    mouth_dist_stabilizer = Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1
    )
    # for body
    body_stabilizers = [Stabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(16)]

    # Initialize TCP connection
    if args.connect:
        socket = init_TCP()

    while cap.isOpened():
        success, img = cap.read()

        if not success:
            print("Ignoring empty camera frame.")
            continue

        # 通过3个步骤进行位姿估计：
        # 1. 检测人脸；
        # 2. 检测标志点；
        # 3. 估计位姿

        # first two steps
        img_facemesh, faces = detector.findFaceMesh(img)
        bodys = bodyDector.findPosition(img_facemesh)


        # 翻转输入图像，使其与facemesh内容匹配
        img = cv2.flip(img, 1)

        bodyFeatures = BodyFeatures()


        if bodys:

            left_arm_points = [bodys[12], bodys[14], bodys[12], bodys[14], bodys[12], bodys[14]]
            if left_arm_points:
                for i in range(len(left_arm_points)):
                    letf_arm_image[i, 0] = left_arm_points[i][0]
                    letf_arm_image[i, 1] = left_arm_points[i][1]

                # 旋转量 平移量
                left_arm_pose = left_arm_pose_estimator.solve_left_arm_pose_by_all_points(letf_arm_image)

                # Stabilize the left arm pose.
                steady_left_arm_pose = []
                # pose[[],[]]降维度->pose[]
                pose_np = np.array(left_arm_pose).flatten()

                for value, ps_stb in zip(pose_np, left_arm_pose_stabilizers):
                    ps_stb.update([value])
                    steady_left_arm_pose.append(ps_stb.state[0])
                steady_left_arm_pose = np.reshape(steady_left_arm_pose, (-1, 3))

                # 计算身体横摇/俯仰/偏航
                left_arm_roll = np.clip(np.degrees(steady_left_arm_pose[0][1]), -90, 90)
                left_arm_pitch = np.clip(-(180 + np.degrees(steady_left_arm_pose[0][0])), -90, 90)
                left_arm_yaw = np.clip(np.degrees(steady_left_arm_pose[0][2]), -90, 90)
                # print(left_arm_roll, left_arm_pitch, left_arm_yaw)


            for i in range(len(body_image_points)):
                body_image_points[i, 0] = bodys[i][0]
                body_image_points[i, 1] = bodys[i][1]

            # 关节角度
            angles = bodyFeatures.findAllAngle(bodys)

            # 身体姿态body_pose_estimator
            bodypose = body_pose_estimator.solve_body_pose_by_all_points(body_image_points)

            # Stabilize the body angle.
            steady_body = []
            for value, bd_stb in zip(angles, body_stabilizers):
                bd_stb.update([value])

                steady_body.append(bd_stb.state[0])
            # 转一维
            steady_body = np.array(steady_body).flatten()
            # print("steady_body", steady_body)

            # Stabilize the body pose.
            steady_bodypose = []
            # bodypose[[],[]]降维度->bodypose[]
            bodypose_np = np.array(bodypose).flatten()

            for value, ps_stb in zip(bodypose_np, body_pose_stabilizers):
                ps_stb.update([value])
                steady_bodypose.append(ps_stb.state[0])
            steady_bodypose = np.reshape(steady_bodypose, (-1, 3))
            # print("steady_bodypose", steady_bodypose[0][0], steady_bodypose[0][1], steady_bodypose[0][2])

            # 计算身体横摇/俯仰/偏航
            body_roll = np.clip(np.degrees(steady_bodypose[0][1]), -90, 90)
            body_pitch = np.clip(-(180 + np.degrees(steady_bodypose[0][0])), -90, 90)
            body_yaw = np.clip(np.degrees(steady_bodypose[0][2]), -90, 90)
            # print(body_roll, body_pitch, body_yaw)

        # 如果检测到任何人脸
        if faces:
            # 只取最大
            for i in range(len(image_points)):
                image_points[i, 0] = faces[0][i][0]
                image_points[i, 1] = faces[0][i][1]

            # 用于优化虹膜周围的地标
            for j in range(len(iris_image_points)):
                iris_image_points[j, 0] = faces[0][j + 468][0]
                iris_image_points[j, 1] = faces[0][j + 468][1]

            # The third step: pose estimation
            # pose: [[rvec], [tvec]]
            # 旋转量，平移量
            pose = pose_estimator.solve_pose_by_all_points(image_points)

            # 虹膜
            x_ratio_left, y_ratio_left = FacialFeatures.detect_iris(image_points, iris_image_points, Eyes.LEFT)
            x_ratio_right, y_ratio_right = FacialFeatures.detect_iris(image_points, iris_image_points, Eyes.RIGHT)

            # 控制研眼睛开闭
            ear_left = FacialFeatures.eye_aspect_ratio(image_points, Eyes.LEFT)
            ear_right = FacialFeatures.eye_aspect_ratio(image_points, Eyes.RIGHT)

            pose_eye = [ear_left, ear_right, x_ratio_left, y_ratio_left, x_ratio_right, y_ratio_right]

            # 嘴开闭
            mar = FacialFeatures.mouth_aspect_ratio(image_points)
            # 嘴大小
            mouth_distance = FacialFeatures.mouth_distance(image_points)

            # Stabilize the pose.
            steady_pose = []
            # pose[[],[]]降维度->pose[]
            pose_np = np.array(pose).flatten()

            for value, ps_stb in zip(pose_np, pose_stabilizers):
                ps_stb.update([value])
                steady_pose.append(ps_stb.state[0])
            steady_pose = np.reshape(steady_pose, (-1, 3))
            # print("steady_pose", steady_pose[0][0],steady_pose[0][1],steady_pose[0][2])

            # stabilize the eyes value
            steady_pose_eye = []
            for value, ps_stb in zip(pose_eye, eyes_stabilizers):
                ps_stb.update([value])
                steady_pose_eye.append(ps_stb.state[0])
            steady_pose_eye = np.reshape(steady_pose_eye, (-1, 2))

            mouth_dist_stabilizer.update([mouth_distance])
            steady_mouth_dist = mouth_dist_stabilizer.state[0]

            # 计算横摇/俯仰/偏航
            roll = np.clip(np.degrees(steady_pose[0][1]), -90, 90)
            pitch = np.clip(-(180 + np.degrees(steady_pose[0][0])), -90, 90)
            yaw = np.clip(np.degrees(steady_pose[0][2]), -90, 90)
            # print(body_roll, body_pitch, body_yaw)


            # pose_estimator.draw_annotation_box(img, pose[0], pose[1], color=(255, 128, 128))

            # pose_estimator.draw_axis(img, pose[0], pose[1])

            # pose_estimator.draw_axes(img_facemesh, steady_pose[0], steady_pose[1])

        else:
            # 重置位姿估计器
            pose_estimator = PoseEstimator((img_facemesh.shape[0], img_facemesh.shape[1]))

        if faces or bodys:
            # send info to unity
            if args.connect:

                # for sending to live2d model (Hiyori)
                # send_info_to_unity(socket,
                #     (roll, pitch, yaw,
                #     ear_left, ear_right, x_ratio_left, y_ratio_left, x_ratio_right, y_ratio_right,
                #     mar, steady_mouth_dist[0])
                # )

                # 包括肢体旋转角
                # send_info_to_unity(socket,
                #                    (roll, pitch, yaw,
                #                     steady_pose_eye[0][0], steady_pose_eye[0][1], steady_pose_eye[1][0],
                #                     steady_pose_eye[1][1], steady_pose_eye[2][0], steady_pose_eye[2][1],
                #                     mar, steady_mouth_dist[0], steady_body[0], steady_body[1], steady_body[2],
                #                     steady_body[3], steady_body[4], steady_body[5], steady_body[6], steady_body[7]
                #                     , steady_body[8], steady_body[9], steady_body[10], steady_body[11]
                #                     , steady_body[12], steady_body[13], steady_body[14], steady_body[15],
                #                     body_roll, body_pitch, body_yaw)
                # )

                # send_info_to_unity(socket,
                #                    (roll, pitch, yaw,
                #                     steady_pose_eye[0][0], steady_pose_eye[0][1], steady_pose_eye[1][0],
                #                     steady_pose_eye[1][1], steady_pose_eye[2][0], steady_pose_eye[2][1],
                #                     mar, steady_mouth_dist[0], body_roll, body_pitch, body_yaw,
                #                     left_arm_roll, left_arm_pitch, left_arm_yaw)
                # )
                if faces and bodys:
                    send_info_to_unity(socket,
                                       (roll, pitch, yaw,
                                        steady_pose_eye[0][0], steady_pose_eye[0][1], steady_pose_eye[1][0],
                                        steady_pose_eye[1][1], steady_pose_eye[2][0], steady_pose_eye[2][1],
                                        mar, steady_mouth_dist[0], body_roll, body_pitch, body_yaw,
                                        steady_body[0], steady_body[1], steady_body[2],
                                        steady_body[3], steady_body[4], steady_body[5])
                                       )
                else:
                    if faces:
                        send_info_to_unity(socket,
                                           (roll, pitch, yaw,
                                            steady_pose_eye[0][0], steady_pose_eye[0][1], steady_pose_eye[1][0],
                                            steady_pose_eye[1][1], steady_pose_eye[2][0], steady_pose_eye[2][1],
                                            mar, steady_mouth_dist[0], 0, 0, 0,
                                            0, 0, 0,
                                            0, 0, 0,)
                                           )
                    else:
                        if bodys:
                            send_info_to_unity(socket,
                                               (0, 0, 0,
                                                0, 0, 0,
                                                0, 0, 0,
                                                0, 0, body_roll, body_pitch, body_yaw,
                                                steady_body[0], steady_body[1], steady_body[2],
                                                steady_body[3], steady_body[4], steady_body[5])
                                               )

                # print the sent values in the terminal
                if args.debug:
                    print_debug_msg((roll, pitch, yaw,
                                     ear_left, ear_right, x_ratio_left, y_ratio_left, x_ratio_right, y_ratio_right,
                                     mar, mouth_distance))
        
        # show self
        cv2.imshow('self', img_facemesh)
        
        # press "q" to leave
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('self', cv2.WND_PROP_VISIBLE) == 0:
            break

    cap.release()


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--connect", action="store_true",
                        help="connect to unity character",
                        default=True)

    parser.add_argument("--port", type=int, 
                        help="specify the port of the connection to unity. Have to be the same as in Unity", 
                        default=5066)

    # parser.add_argument("--cam", type=int,
    #                     help="specify the camera number if you have multiple cameras",
    #                     default=0)

    parser.add_argument("--debug", action="store_true",
                        help="showing raw values of detection in the terminal",
                        default=False)

    args = parser.parse_args()
    # demo code
    main()
