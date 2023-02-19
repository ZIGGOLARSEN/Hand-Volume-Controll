from ctypes import POINTER, cast
from functools import partial

import cv2
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from .hand_detector import HandDetector
from .video_capture import VideoCapture


class VolumeController:
    min_length = 35
    max_length = 300

    def __init__(self, max_hands=1, draw_landmarks=False) -> None:
        self.detector = HandDetector(max_hands)
        self.capture = VideoCapture('Volume Cotroller')
        self.thumb_and_pointer_coords = {}
        self.draw_landmarks = draw_landmarks

    def start(self) -> None:
        self.volume_setup()
        self.capture.add_event(partial(self.detector.find_hands, draw_landmarks=self.draw_landmarks))
        self.capture.add_event(self.track_thumb_and_pointer)
        self.capture.add_event(self.draw_connecting_line)
        self.capture.add_event(self.get_length_of_the_lines)
        self.capture.add_event(self.control_volume)
        self.capture.add_event(self.detector.clear_hands_and_landmarks)
        self.capture.start()

    def track_thumb_and_pointer(self, img) -> None:
        if not hasattr(self.detector, 'hands_and_landmarks'): return

        for hand, landmarks in self.detector.hands_and_landmarks.items():
            self.thumb_and_pointer_coords[hand] = {}
            for id, x, y in landmarks:
                if id==4 or id==8:
                    cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                    self.thumb_and_pointer_coords[hand][id] = (x, y)

    def draw_connecting_line(self, img) -> None:
        if not self.thumb_and_pointer_coords: return

        for hand in self.thumb_and_pointer_coords.values():
            thumb, pointer = hand.values()

            # to avoid leftover lines after we hide hands from camera
            if not self.detector.hands_and_landmarks: return
            cv2.line(img, thumb, pointer, (255, 0, 255), 2)

    def get_length_of_the_lines(self, img) -> None:
        self.lengths = {}
        for hand_id, value in self.thumb_and_pointer_coords.items():
            (x_1, y_1), (x_2, y_2) = value.values()
            # distance formula
            length = np.sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
            self.lengths[hand_id] = length

    def volume_setup(self) -> None:
        # boilerplate code for setting up programatical volume control 
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def control_volume(self, img) -> None:
        min_vol, max_vol, _ = self.volume.GetVolumeRange()

        if not self.lengths.values(): return

        volume = round(np.interp(self.lengths[0], [self.min_length, self.max_length], [min_vol, max_vol]), 2)

        percentage_vol = np.interp(volume, [min_vol, max_vol], [0, 100])
        vol_bar = int(np.interp(percentage_vol, [0, 100], [400, 150]))

        # code for bar that shows percentage volume at that time
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, vol_bar), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(percentage_vol)}%', (50, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        self.volume.SetMasterVolumeLevel(volume, None)


vol_controller = VolumeController()

vol_controller.start()
