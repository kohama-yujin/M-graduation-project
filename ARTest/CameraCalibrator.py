import cv2
import numpy as np
import os
import argparse


class CameraCalibrator:
    """
    カメラの内部パラメータを求めるクラス
    チェスボードパターンを使ってキャリブレーションを行う
    """

    def __init__(self, cols, rows, square_size, image_dir, save_path):
        """
        Parameters:
            cols (int): チェスボードの列数（内側の交点数）
            rows (int): チェスボードの行数（内側の交点数）
            square_size (float): マスの1辺の実際の長さ（cm）
            image_dir: 入力画像のフォルダパス
            save_path: キャリブレーション結果の保存パス
        """

        # チェスボードのサイズとマスのサイズを設定
        self.chessboard_size = (cols, rows)
        self.square_size = square_size
        self.image_dir = image_dir
        self.save_path = save_path

        # チェスボードの3D座標を生成
        objp = np.zeros((cols * rows, 3), np.float32)  # 3D座標を格納する配列
        objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)  # XYに正規化(Zを削除)
        objp *= square_size  # スケーリング
        self.objp = objp  # 3D 座標群

        # 3D座標と2D座標を格納するリスト
        self.objpoints = []
        self.imgpoints = []

        # 内部パラメータ
        self.camera_matrix = None  # カメラ行列
        self.dist_coeffs = None  # 歪み係数

    def calibrate(self):
        """
        キャリブレーションを実行する関数
        """
        pass

    def get_intrinsic_parameters(self):
        """
        内部パラメータを取得する関数
        """

        # キャリブレーション画像の読み込み
        for image_name in os.listdir(self.image_dir):
            img_path = os.path.join(self.image_dir, image_name)
            img = cv2.imread(img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # チェスボード検出
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
            if ret:
                # 各画像の3次元座標と2次元座標を追加
                self.objpoints.append(self.objp)
                self.imgpoints.append(corners)

                # コーナー描画（確認用）
                cv2.drawChessboardCorners(img, self.chessboard_size, corners, ret)
                cv2.imshow("Corners", img)
                cv2.waitKey(0)
        cv2.destroyAllWindows()

        # キャリブレーション
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints,  # 3次元座標群（ワールド座標系）
            self.imgpoints,  # 2次元座標群（ピクセル座標）
            gray.shape[::-1],  # 画像サイズ（幅、高さ）
            None,  # 初期のカメラ行列（Noneなら自動推定）
            None,  # 初期の歪み係数（Noneなら自動推定）
        )
        if ret:
            self.camera_matrix = camera_matrix
            self.dist_coeffs = dist_coeffs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camera Calibration Tool")
    # 以下、必須入力
    parser.add_argument(
        "--cols", type=int, required=True, help="Number of inner corners (columns)"
    )
    parser.add_argument(
        "--rows", type=int, required=True, help="Number of inner corners (rows)"
    )
    parser.add_argument(
        "--square_size",
        type=float,
        required=True,
        help="Size of one square (e.g. in cm)",
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        required=True,
        help="Directory of calibration images",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        required=True,
        help="Path to save calibration result",
    )

    args = parser.parse_args()

    calibrator = CameraCalibrator(
        cols=args.cols,
        rows=args.rows,
        square_size=args.square_size,
        image_dir=args.image_dir,
        save_path=args.save_path,
    )

    # 内部パラメータ（）の計算
    calibrator.get_intrinsic_parameters()
    print(calibrator.camera_matrix)

    # calibrator.calibrate()
    # calibrator.print_result()
    # calibrator.save(args.save_path)
    # print(f"\nCalibration data saved to '{args.save_path}'")
