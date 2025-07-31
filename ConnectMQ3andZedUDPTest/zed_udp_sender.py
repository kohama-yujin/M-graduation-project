import pyzed.sl as sl
import cv2
import socket
import time
import struct

# UDP設定
# ip = "192.168.137.47" # 受信側のIPアドレス（gpu_win接続時）
# ip = "133.15.35.66"  # 受信側のIPアドレス
# ip = "192.168.2.155"  # 受信側のIPアドレス
ip = "127.0.0.1"  # ローカルアドレス
port = 12345  # 受信側と合わせる
CHUNK_SIZE = 4096  # 4KBずつ送信

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ZEDカメラの初期化
zed = sl.Camera()
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720  # 解像度（HD720, HD1080, etc）
init_params.depth_mode = sl.DEPTH_MODE.NONE          # 深度不要な場合
 # カメラ起動
status = zed.open(init_params)
if status != sl.ERROR_CODE.SUCCESS:
    print("カメラを開けませんでした:", status)
    exit()
# 画像取得のためのオブジェクト
image = sl.Mat()

try:
    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)  # 左目画像を取得
            frame = image.get_data()  # numpy配列に変換（BGR）

            # JPEG圧縮
            _, encoded_img = cv2.imencode(".jpg", frame)
            data = encoded_img.tobytes()

            # パケット数を先に送信
            num_packets = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE
            sock.sendto(str(num_packets).encode(), (ip, port))
            print(f"Num Packets : {num_packets}")
            time.sleep(0.01)  # 少し待機（受信側の準備のため）

            # チャンク送信
            for i in range(num_packets):
                chunk = data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
                pkt = struct.pack("!I", i) + chunk  #  # パケット番号を付加
                sock.sendto(pkt, (ip, port))
                time.sleep(0.001)  # 送信間隔を少し空けると安定しやすい

            time.sleep(0.001)

finally:
    print(frame.dtype, frame.shape)
    zed.close()
    sock.close()
