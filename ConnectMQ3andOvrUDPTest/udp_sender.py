import cv2
import socket

# UDP設定
ip = "133.15.35.42"  # 受信側のIPアドレス
port = 12345  # 受信側と合わせる
CHUNK_SIZE = 4096  # 4KBずつ送信

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

frame_count = 0
cap = cv2.VideoCapture(1)  # カメラ起動
# while True:
ret, frame = cap.read()  # 画像読み込み
# if not ret:
#     break

# 解像度下げて送信サイズを抑える
frame = cv2.resize(frame, (320, 240))

# JPEG圧縮
_, encoded_img = cv2.imencode(".jpg", frame)
data = encoded_img.tobytes()
print(f"Sent frame {frame_count}, size: {len(encoded_img)} bytes")

# パケット数を先に送信
num_packets = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"Num Packets {num_packets}")

sock.sendto(str(num_packets).encode(), (ip, port))

# チャンク送信
for i in range(num_packets):
    chunk = data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
    sock.sendto(chunk, (ip, port))
frame_count += 1

cap.release()
message = "こんにちは！".encode("utf-8")
sock.sendto(message, ("127.0.0.1", port))
sock.close()
