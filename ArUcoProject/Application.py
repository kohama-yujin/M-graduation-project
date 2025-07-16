import numpy as np
import datetime
import cv2
from cv2 import aruco
from OpenGL.GL import *
import glfw

import USBCamera as cam
import GLWindow
import PoseEstimation as ps


#
# MRアプリケーションクラス
#
class Application:

    # ------------------------------------------------------------------------
    # コンストラクタ
    # ------------------------------------------------------------------------
    # @param width    : 画像の横サイズ
    # @param height   : 画像の縦サイズ
    # @param deviceID : カメラ番号
    #
    def __init__(self, title, width, height, deviceID, use_api):
        if deviceID != -1:
            self.use_camera = True
        else:
            self.use_camera = False

        # 画像の大きさ設定
        self.width = width
        self.height = height
        self.channel = 3

        # カメラの設定
        if self.use_camera:
            self.camera = cam.USBCamera(deviceID, width, height, use_api)

        # GLウィンドウの設定
        self.glwindow = GLWindow.GLWindow(
            title, width, height, self.display_func, self.keyboard_func
        )

        # カメラの内部パラメータ
        self.focus = 700.0
        self.u0 = width / 2.0
        self.v0 = height / 2.0

        # OpenGLの表示パラメータ
        scale = 0.01
        self.viewport_horizontal = self.u0 * scale
        self.viewport_vertical = self.v0 * scale
        self.viewport_near = self.focus * scale
        self.viewport_far = self.viewport_near * 1.0e6
        self.modelview = (GLfloat * 16)()
        self.draw_axis = True
        self.use_normal = False

        # カメラ姿勢を推定するクラス変数
        self.estimator = ps.PoseEstimation(self.focus, self.u0, self.v0)

        # ファイル出力数のカウント用変数
        self.count = 0

        # Arucoマーカーの設定
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.aruco_parameters = aruco.DetectorParameters()
        #        self.aruco_parameters = aruco.DetectorParameters_create()
        self.ids = None
        self.corners = ()

    # ------------------------------------------------------------------------
    # カメラの内部パラメータの設定関数
    # ------------------------------------------------------------------------
    def SetCameraParam(self, focus, u0, v0):
        self.focus = focus
        self.u0 = u0
        self.v0 = v0

    # ------------------------------------------------------------------------
    # カメラ映像を表示するための関数
    #
    # ここに作成するアプリケーションの大部分の処理を書く
    # ------------------------------------------------------------------------
    def display_func(self, window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 画像の読み込み
        success = False
        if self.use_camera:
            success, self.image = self.camera.CaptureImage()
        else:
            self.image = self.glwindow.image

        if not success:
            return

        # マーカ検出
        self.corners, self.ids, _ = aruco.detectMarkers(
            self.image, self.aruco_dict, parameters=self.aruco_parameters
        )
        # マーカの描画
        self.image = aruco.drawDetectedMarkers(self.image, self.corners, self.ids)
        # 画像の描画
        self.glwindow.draw_image(self.image)

        # カメラ姿勢推定
        if self.ids is not None:
            success = self.compute_camera_pose()
            if success:
                # 3次元モデルの描画
                self.draw_3D_model()

        glfw.swap_buffers(window)

    # ------------------------------------------------------------------------
    # キー関数
    # ------------------------------------------------------------------------
    def keyboard_func(self, window, key, scancode, action, mods):
        # Qで終了
        if key == glfw.KEY_Q:
            glfw.set_window_should_close(self.glwindow.window, GL_TRUE)

        # Sで画像の保存
        if action == glfw.PRESS and key == glfw.KEY_S:
            self.save_image(self.count)
            self.count += 1

        # Rで動画の保存
        if action == glfw.PRESS and key == glfw.KEY_R:
            if self.camera.video_out == False:
                self.camera.VideoOutStart()
            else:
                self.camera.VideoOutEnd()

        # Tでランドマーク表示を切り替え
        if action == glfw.PRESS and key == glfw.KEY_T:
            self.set_draw_landmark(not self.hand_detection.draw_landmark)

    # ------------------------------------------------------------------------
    # 画像を保存する関数
    # ------------------------------------------------------------------------
    def save_image(self, count):
        filename = "output_image-%05d.png" % count
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        glReadBuffer(GL_BACK)
        glReadPixels(
            0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, image.data
        )
        image = cv2.flip(image, 0)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filename, image)

    # ------------------------------------------------------------------------
    # 画面録画を保存する関数
    # ------------------------------------------------------------------------
    def save_record(self):
        filename = "output_video.mp4"
        fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        video = cv2.VideoWriter(filename, fourcc, fps, (self.width, self.height))
        video = self.camera.SaveRecord(filename)
        print("録画を開始します..." + filename)
        return video

    # ------------------------------------------------------------------------
    # mediapipeで検出した手のランドマークを描画するかを設定する関数
    # ------------------------------------------------------------------------
    def set_draw_landmark(self, draw_flag):
        self.hand_detection.set_draw_landmarks(draw_flag)

    # ------------------------------------------------------------------------
    # 3次元モデルをセットする関数
    # ------------------------------------------------------------------------
    def set_mqo_model(self, model):
        self.model = model

    # ------------------------------------------------------------------------
    # カメラ姿勢を推定する関数
    # ------------------------------------------------------------------------
    def compute_camera_pose(self):
        c = self.corners[0][0]
        x1, x2, x3, x4 = c[:, 0]
        y1, y2, y3, y4 = c[:, 1]

        point_2D = np.array([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], dtype="double")

        # カメラ姿勢を計算
        success, R, t = self.estimator.compute_camera_pose(point_2D)

        if success:
            # 世界座標系に対するカメラ位置を計算
            #     この位置を照明位置として使用
            if self.use_normal:
                pos = -R.transpose().dot(t)
                self.camera_pos = np.array(
                    [pos[0], pos[1], pos[2], 1.0], dtype="double"
                )
            # OpenGLで使用するモデルビュー行列を生成
            self.modelview[0] = R[0][0]
            self.modelview[1] = R[1][0]
            self.modelview[2] = R[2][0]
            self.modelview[3] = 0.0
            self.modelview[4] = R[0][1]
            self.modelview[5] = R[1][1]
            self.modelview[6] = R[2][1]
            self.modelview[7] = 0.0
            self.modelview[8] = R[0][2]
            self.modelview[9] = R[1][2]
            self.modelview[10] = R[2][2]
            self.modelview[11] = 0.0
            self.modelview[12] = t[0]
            self.modelview[13] = t[1]
            self.modelview[14] = t[2]
            self.modelview[15] = 1.0

        return success

    # ------------------------------------------------------------------------
    # カメラ姿勢を推定する関数
    # ------------------------------------------------------------------------
    def draw_3D_model(self):
        self.glwindow.push_GL_setting()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(
            -self.viewport_horizontal,
            self.viewport_horizontal,
            -self.viewport_vertical,
            self.viewport_vertical,
            self.viewport_near,
            self.viewport_far,
        )
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glLoadMatrixf(self.modelview)

        # 証明をオン
        if self.use_normal:
            glLightfv(GL_LIGHT0, GL_POSITION, self.camera_pos)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

        model_shift_X = 0.0
        model_shift_Y = 0.0
        model_shift_Z = 0.0

        glTranslatef(model_shift_X, model_shift_Y, model_shift_Z)
        glScalef(self.model.scale, self.model.scale, self.model.scale)
        self.model.draw()

        self.glwindow.pop_GL_setting()

        # 証明をオフ
        if self.use_normal:
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
