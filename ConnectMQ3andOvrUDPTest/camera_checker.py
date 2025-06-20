import cv2

cap = cv2.VideoCapture(1)  # Ovrvision Proがデバイス1にある場合

while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラからのフレーム取得に失敗しました。")
        break
    cv2.imshow("Ovrvision Camera", frame)
    if cv2.waitKey(1) == 27:  # ESCキーで終了
        print("カメラチェックを終了します。")
        break

print(frame.dtype, frame.shape)
cap.release()
cv2.destroyAllWindows()
