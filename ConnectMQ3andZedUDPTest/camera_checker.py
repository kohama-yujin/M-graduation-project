import cv2

cap = cv2.VideoCapture(0)
# 解像度設定
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera Check", frame)
    if cv2.waitKey(1) == 27:  # ESCキーで終了
        print("カメラチェックを終了します。")
        break

print(frame.dtype, frame.shape)
cap.release()
cv2.destroyAllWindows()
