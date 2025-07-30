import pyzed.sl as sl
import cv2

# ZEDカメラの初期化
zed = sl.Camera()
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720  # 解像度（HD720, HD1080, etc）
init_params.depth_mode = sl.DEPTH_MODE.NONE          # 深度不要な場合

status = zed.open(init_params)
if status != sl.ERROR_CODE.SUCCESS:
    print("カメラを開けませんでした:", status)
    exit()

# 画像取得のためのオブジェクト
image = sl.Mat()

while True:
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT)  # 左目画像を取得
        frame = image.get_data()  # numpy配列に変換（BGR）

        cv2.imshow("ZED Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

zed.close()
cv2.destroyAllWindows()
