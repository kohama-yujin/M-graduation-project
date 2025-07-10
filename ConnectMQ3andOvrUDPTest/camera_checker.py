import cv2
import numpy as np

cap = cv2.VideoCapture(1)
# 解像度設定
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # VideoCaptureは8bitが限界
    # 本来の16bitを8bitに圧縮して取得（重なる）
    # 上位8bit：左目のグレイスケール
    # 下位8bit：右目のBayer
    unit8 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Bayer補間でカラー化
    color = cv2.cvtColor(unit8, cv2.COLOR_BAYER_GB2BGR)

    cv2.imshow("Right Eye - Color Only", frame)

    # cv2.imshow("Ovrvision Camera", frame)
    if cv2.waitKey(1) == 27:  # ESCキーで終了
        print("カメラチェックを終了します。")
        break

print(frame.dtype, frame.shape)
cap.release()
cv2.destroyAllWindows()
