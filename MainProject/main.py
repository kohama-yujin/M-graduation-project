import cv2
import time
from CameraCalibrator import CameraCalibrator


def main():
    # カメラ読み込み
    cap = cv2.VideoCapture(0)
    # 解像度設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 動画出力設定（MP4形式）
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # ※重要
    out = cv2.VideoWriter("output.mp4", fourcc, 30.0, (1280, 720))

    # カメラキャリブレーション
    calibrator = CameraCalibrator(9, 6, 1.27, "./calib_images")
    calibrator.calibrate()

    # カメラチェック
    while True:
        ret, frame = cap.read()
        # 画像が取得できなかった場合は終了
        if not ret:
            break

        # 画像を入力
        # frame = cv2.imread("./input.jpg")
        # 姿勢推定
        calibrator.estimate_pose(frame)
        # AR描画
        ret, result_frame = calibrator.draw_axis()
        if ret:
            out.write(result_frame)  # 動画保存
            cv2.imshow("Camera Check", result_frame)
            time.sleep(0.02)
            if cv2.waitKey(1) == 27:  # ESCキーで終了
                print("カメラチェックを終了します。")
                break
    # 後片付け
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
