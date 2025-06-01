import cv2

cap = cv2.VideoCapture(1)  # Ovrvision Proがデバイス1にある場合

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Ovrvision Camera", frame)
    if cv2.waitKey(1) == 27:  # ESCキーで終了
        break

cap.release()
cv2.destroyAllWindows()
