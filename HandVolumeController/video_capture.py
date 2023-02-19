import cv2
import time

class VideoCapture:

    def __init__(self, title, quit_key='q', port_number=0, fps_coords=(10, 70)) -> None:
        self.cap = cv2.VideoCapture(port_number)
        self.title = title
        self.quit_key = quit_key
        self.fps_coords = fps_coords
        
        self.previous_time = 0
        self.events = []

    def start(self) -> None:
        while True:
            _, img = self.cap.read()

            fps = self.track_fps()

            self.excecute_events(img)

            if self.fps_coords:
                cv2.putText(img, f'fps: {fps}', self.fps_coords, cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

            cv2.imshow(self.title, img)

            if cv2.waitKey(1) == ord(self.quit_key):
                break
        self.close()

    def close(self) -> None:
        self.cap.release()
        cv2.destroyAllWindows()

    def track_fps(self) -> int:
        current_time = time.time()
        fps = 1 / (current_time - self.previous_time)
        self.previous_time = current_time

        return int(fps)

    def add_event(self, event) -> None:
        # every event that gets added to the events array will be excecuted in order during while loop
        # one restriction to the events is that it must have only one argument to recieve - img.
        # The main reason for this is compatibility for other events so user must take into account that event 
        # design is restricted and must get around that so that this module can be used for different tasks 
        # without adjusting code
        self.events.append(event)

    def excecute_events(self, img) -> None:
        for event in self.events:
            event(img)
