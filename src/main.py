import cv2

# Load the video
video = cv2.VideoCapture("data/videos/sample.mp4")

# Read video frame by frame
while True:
    ret, frame = video.read()

    if not ret:
        break

    cv2.imshow("AI Surveillance", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()