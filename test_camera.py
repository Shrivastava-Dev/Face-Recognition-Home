import cv2

cap = cv2.VideoCapture(1)  # USB Camera

if not cap.isOpened():
    print("Cannot access camera")
    exit()

print("Camera working! Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow('Test Camera - Press Q to quit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()