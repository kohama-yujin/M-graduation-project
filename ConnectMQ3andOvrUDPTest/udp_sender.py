import cv2
import socket
import time
import struct

# UDP設定
# ip = "133.15.35.72"  # 受信側のIPアドレス
ip = "192.168.2.155"  # 受信側のIPアドレス
# ip = "127.0.0.1"  # ローカルアドレス
port = 12345  # 受信側と合わせる
CHUNK_SIZE = 4096  # 4KBずつ送信

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(1)  # カメラ起動

try:
    while True:
        ret, frame = cap.read()  # 画像読み込み
        if not ret:
            break

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
        print(f"Frame sent successfully!")

        time.sleep(0.001)
        # break

finally:
    cap.release()
    sock.close()
