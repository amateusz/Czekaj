import sys
import statistics

sys.path.append('/usr/lib/python3.7/site-packages/')  # <333
import cv2

cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

positions = [[], []]
sizes = []

avg_len = 25

while True:

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(120, 120),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if len(positions) > avg_len:
            positions.pop(0)
        if len(sizes) > avg_len:
            sizes.pop(0)
        positions[0].append(x)
        positions[1].append(y)

        sizes.append((w + h) / 2)
        # calc deltas
        size_delta = sizes[len(sizes) - 1] - statistics.mean(sizes)
        size_delta = size_delta / 90.0
        position_x_delta = float(positions[0][len(positions[0]) - 1] - statistics.mean(positions[0]))
        position_y_delta = float(positions[1][len(positions[1]) - 1] - statistics.mean(positions[1]))

        position_x_delta /= float(frame.shape[1])
        position_x_delta = abs(position_x_delta)

        position_y_delta /= float(frame.shape[0])
        position_y_delta = abs(position_y_delta)

    if len(faces) > 0:
        # print(size_delta, end='\t')
        # print(position_x_delta)
        heat = sum([size_delta, position_x_delta, position_y_delta])
        heat = min(1.0, heat)
        heat = max(0.0, heat)
    else:
        # positions = []
        # sizes = [0,] * 20
        heat = 0.0
    print(heat)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
