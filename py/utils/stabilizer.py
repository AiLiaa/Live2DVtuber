"""
使用卡尔曼滤波器作为点稳定器来稳定2D点。
"""
import numpy as np

import cv2

class Stabilizer:
    """使用卡尔曼滤波器作为点稳定器."""

    def __init__(self,
                 state_num=4, # 状态的维度
                 measure_num=2, # 测量的维度
                 cov_process=0.0001,
                 cov_measure=0.1):

        # 目前只支持标量和点，因此请先检查用户输入
        assert state_num == 4 or state_num == 2, "Only scalar and point supported, Check state_num please."

        # 存储参数
        self.state_num = state_num
        self.measure_num = measure_num

        # filter
        self.filter = cv2.KalmanFilter(state_num, measure_num, 0)

        # 存储状态
        self.state = np.zeros((state_num, 1), dtype=np.float32)

        # 存储测量结果
        self.measurement = np.array((measure_num, 1), np.float32)

        # 存储预测值
        self.prediction = np.zeros((state_num, 1), np.float32)

        '''
        Kalman这个类需要初始化下面变量：
        转移矩阵，测量矩阵，控制向量(没有的话，就是0)，
        过程噪声协方差矩阵，测量噪声协方差矩阵，
        后验错误协方差矩阵，前一状态校正后的值，当前观察值。
            在此cv2.KalmanFilter(4,2)表示转移矩阵维度为4，测量矩阵维度为2
        卡尔曼滤波模型假设k时刻的真实状态是从(k − 1)时刻的状态演化而来，符合下式：
                    X(k) = F(k) * X(k-1) + B(k)*U(k) + W（k）
        其中
        F(k)  是作用在xk−1上的状态变换模型（/矩阵/矢量）。 
        B(k)  是作用在控制器向量uk上的输入－控制模型。 
        W(k)  是过程噪声，并假定其符合均值为零，协方差矩阵为Qk的多元正态分布。
        '''

        # 标量的卡尔曼参数设置
        if self.measure_num == 1:
            # 设置转移矩阵
            self.filter.transitionMatrix = np.array([[1, 1],
                                                     [0, 1]], np.float32)
            # 设置测量矩阵
            self.filter.measurementMatrix = np.array([[1, 1]], np.float32)
            # 设置过程噪声协方差矩阵
            self.filter.processNoiseCov = np.array([[1, 0],
                                                    [0, 1]], np.float32) * cov_process
            # 设置测量协方差矩阵
            self.filter.measurementNoiseCov = np.array(
                [[1]], np.float32) * cov_measure

        # 点的卡尔曼参数设置
        if self.measure_num == 2:
            self.filter.transitionMatrix = np.array([[1, 0, 1, 0],
                                                     [0, 1, 0, 1],
                                                     [0, 0, 1, 0],
                                                     [0, 0, 0, 1]], np.float32)

            self.filter.measurementMatrix = np.array([[1, 0, 0, 0],
                                                      [0, 1, 0, 0]], np.float32)

            self.filter.processNoiseCov = np.array([[1, 0, 0, 0],
                                                    [0, 1, 0, 0],
                                                    [0, 0, 1, 0],
                                                    [0, 0, 0, 1]], np.float32) * cov_process

            self.filter.measurementNoiseCov = np.array([[1, 0],
                                                        [0, 1]], np.float32) * cov_measure

    def update(self, measurement):

        # 进行卡尔曼预测 predict方法得到状态的预测值矩阵，用来估算目标位置
        self.prediction = self.filter.predict()

        # 当前测量坐标值
        if self.measure_num == 1:
            self.measurement = np.array([[np.float32(measurement[0])]])
        else:
            self.measurement = np.array([[np.float32(measurement[0])],
                                         [np.float32(measurement[1])]])

        # 根据测量结果进行校正
        self.filter.correct(self.measurement)

        # 更新状态值
        self.state = self.filter.statePost

    def set_q_r(self, cov_process=0.1, cov_measure=0.001):
        """
        为processNoiseCov和measurementNoiseCov设置新值
        """

        if self.measure_num == 1:
            self.filter.processNoiseCov = np.array([[1, 0],
                                                    [0, 1]], np.float32) * cov_process
            self.filter.measurementNoiseCov = np.array(
                [[1]], np.float32) * cov_measure
        else:
            self.filter.processNoiseCov = np.array([[1, 0, 0, 0],
                                                    [0, 1, 0, 0],
                                                    [0, 0, 1, 0],
                                                    [0, 0, 0, 1]], np.float32) * cov_process
            self.filter.measurementNoiseCov = np.array([[1, 0],
                                                        [0, 1]], np.float32) * cov_measure


def main():
    """Test code"""
    global mp
    mp = np.array((2, 1), np.float32)  # measurement

    def onmouse(k, x, y, s, p):
        global mp
        mp = np.array([[np.float32(x)], [np.float32(y)]])

    cv2.namedWindow("kalman")
    cv2.setMouseCallback("kalman", onmouse)
    kalman = Stabilizer(4, 2)
    frame = np.zeros((480, 640, 3), np.uint8)  # drawing canvas

    while True:
        kalman.update(mp)
        point = kalman.prediction
        state = kalman.filter.statePost
        cv2.circle(frame, (int(state[0]), int(state[1])), 2, (255, 0, 0), -1)
        cv2.circle(frame, (int(point[0]), int(point[1])), 2, (0, 255, 0), -1)
        cv2.imshow("kalman", frame)
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break


if __name__ == '__main__':
    main()
