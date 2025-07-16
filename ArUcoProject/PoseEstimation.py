import numpy as np
import cv2


#
# 平面上の特徴点対応からカメラ姿勢を推定するクラス
#
class PoseEstimation:

    # ------------------------------------------------------------------------
    # コンストラクタ
    # ------------------------------------------------------------------------
    def __init__(self, f, u0, v0):
        # 投影行列
        self.A = np.array([[f, 0.0, u0], [0.0, f, v0], [0.0, 0.0, 1.0]], dtype="double")

        # 歪み係数
        self.dist_coeff = np.zeros((4, 1))

        # 3次元点と2次元点データ
        self.point_3D = np.array([])
        self.point_2D = np.array([])

        # 推定可能かどうかを表すフラグ
        self.ready = False

    # ------------------------------------------------------------------------
    # カメラ姿勢の推定関数
    # ------------------------------------------------------------------------
    def compute_camera_pose(self, point_2D):
        if self.ready:
            self.point_2D = point_2D
            success, vec_R, t = cv2.solvePnP(
                self.point_3D, self.point_2D, self.A, self.dist_coeff, flags=0
            )
            R = cv2.Rodrigues(vec_R)[0]

            # OpenGLの座標系に変換する回転行列
            R_ = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
            R = np.dot(R_, R)
            t = np.dot(R_, t)

            return True, R, t
        else:
            return False, None, None

    # ------------------------------------------------------------------------
    # 3次元点をセットする関数
    # ------------------------------------------------------------------------
    def set_3D_points(self, point_3D):
        self.point_3D = point_3D
        self.ready = True
