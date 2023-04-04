import cv2
import mediapipe as mp
import time
import math
'''
身体关键点
'''

class BodyPoseDetector():
    def __init__(self, mode=False, upBody=False, enable=False, smooth=True,detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.enable = enable
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        # STATIC_IMAGE_MODE：设置为 false，将输入图像视为视频流
        # PPER_BODY_ONLY：是要追踪33个地标的全部姿势地标还是只有25个上半身的姿势地标。false全身
        # SMOOTH_SEGMENTATION：设置为true，过滤不同的输入图像上的分割掩码以减少抖动
        # MIN_DETECTION_CONFIDENCE：来自人员检测模型的最小置信值 ([0.0, 1.0])，用于将检测视为成功。默认为 0.5。
        # MIN_TRACKING_CONFIDENCE：来自地标跟踪模型的最小置信值 ([0.0, 1.0])，用于将被视为成功跟踪的姿势地标，
        # 否则将在下一个输入图像上自动调用人物检测。将其设置为更高的值可以提高解决方案的稳健性，但代价是更高的延迟
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.enable, self.smooth, self.detectionCon, self.trackCon)

    # 获取动作
    def findPose(self, img, draw=True):
        # 灰度图
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        # print(results.pose_landmarks) # 坐标的三个轴

        if self.results.pose_landmarks:
            if draw:
                # 画出所有节点连线
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    # 获取点的位置
    def findPosition(self, img, draw=True):
        self.lmList = []
        # 灰度图
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img.flags.writeable = False
        self.results = self.pose.process(imgRGB)
        img.flags.writeable = True

        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                # 图片的长、宽、通道
                h, w, c = img.shape
                # print(id, lm)
                # 计算在窗口的位置
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                               self.mpPose.POSE_CONNECTIONS)
        return self.lmList

    # 获取肢体角度 test
    def findAngle(self, img, p1, p2, p3, draw=True):
        # 获取标记点
        x1, y1 = self.lmList[p1]
        x2, y2 = self.lmList[p2]
        x3, y3 = self.lmList[p3]
        # 计算
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
        # print(angle)
        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

# test
def main():
    # 开本机摄像头
    cap = cv2.VideoCapture(0)
    pTime = 0
    # 初始对象
    bodydetector = BodyPoseDetector()
    while True:
        # 读取视频流
        success, img = cap.read()

        img = bodydetector.findPose(img)
        lmList = bodydetector.findPosition(img, draw=False)
        # if len(lmList) != 0:
        #     print(lmList[14])
        #     cv2.circle(img, (lmList[14][0], lmList[14][1]), 15, (0, 0, 255), cv2.FILLED)
        print(bodydetector.findAngle(img, 15, 13, 11))
        # 计算帧数
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(10)
        if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) == 0:
            break
            cv2.destroyAllWindows()


if __name__ == "__main__":
    print("body main")
    main()
