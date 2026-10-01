import cv2

for i in range(5):  # checks indexes 0 to 4
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera index {i} is available")
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f'Camera {i}', frame)
            cv2.waitKey(2000)  # shows for 2 seconds
            cv2.destroyAllWindows()
    cap.release()