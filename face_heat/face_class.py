import sys
import statistics

sys.path.append('/usr/lib/python3.7/site-packages/')  # <333
import cv2


class Heat_Face():
    def __init__(self, cascPath, camPath):

        self.faceCascade = cv2.CascadeClassifier(cascPath)
        __class__.video_capture = cv2.VideoCapture(camPath)
        self.positions = [[], []]
        self.sizes = []
        self.avg_len = 25

    def get_heat(self):

        # Capture frame-by-frame
        ret, self.frame = __class__.video_capture.read()

        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=20,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces[:1]:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if len(self.positions) > self.avg_len:
                self.positions.pop(0)
            if len(self.sizes) > self.avg_len:
                self.sizes.pop(0)
            self.positions[0].append(x)
            self.positions[1].append(y)

            self.sizes.append((w + h) / 2)
            # calc deltas
            size_delta = self.sizes[len(self.sizes) - 1] - statistics.mean(self.sizes)
            size_delta = size_delta / 120.0
            position_x_delta = float(self.positions[0][len(self.positions[0]) - 1] - statistics.mean(self.positions[0]))
            position_y_delta = float(self.positions[1][len(self.positions[1]) - 1] - statistics.mean(self.positions[1]))

            position_x_delta /= float(self.frame.shape[1])
            position_x_delta = abs(position_x_delta)

            position_y_delta /= float(self.frame.shape[0])
            position_y_delta = abs(position_y_delta)

        if len(faces) > 0:
            # print(size_delta, end='\t')
            # print(position_x_delta)
            heat = sum([size_delta, position_x_delta, position_y_delta])
            heat = min(1.0, heat)
            heat = max(0, heat)
        else:
            # positions = []
            # sizes = [0,] * 20
            heat = 0.0

        return heat

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.__del__()

    def display(self):
        # Display the resulting frame
        cv2.imshow('Video', self.frame)
        cv2.waitKey(1)

    def draw_heat(self, heat):
        h, w, ignore = self.frame.shape
        heat_h = int(heat * h)
        cv2.rectangle(self.frame, (w // 7, h), (w // 4, h - heat_h), (0, 100, 255), -1)

    def __del__(self):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.__del__()
        # When everything is done, release the capture
        try:
            self.video_capture.release()
            cv2.destroyAllWindows()
        except:
            pass


if __name__ == '__main__':
    face = Heat_Face('haarcascade_frontalface_default.xml', '/dev/video0')
    while (True):
        heat = face.get_heat()
        print(f'heat: {heat}')
        face.draw_heat(heat)
        face.display()
