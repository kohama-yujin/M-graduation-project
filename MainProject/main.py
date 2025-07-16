import cv2
from CameraCalibrator import CameraCalibrator


def main():
    background_img = cv2.imread("./input.jpg")

    calibrator = CameraCalibrator(9, 6, 1.27, "./calib_images")

    calibrator.calibrate()
    calibrator.estimate_pose(background_img)
    ret, img = calibrator.draw_axis()
    if ret:
        cv2.imwrite("./output.jpg", img)


if __name__ == "__main__":
    main()
