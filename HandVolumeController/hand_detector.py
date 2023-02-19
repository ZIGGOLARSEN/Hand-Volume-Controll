import cv2
import mediapipe as mp
import numpy as np

class HandDetector:

    def __init__(self, max_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) -> None:
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands, 
            min_detection_confidence=min_detection_confidence, 
            min_tracking_confidence=min_tracking_confidence
        )

        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw_landmarks=True) -> None:
        # transform image for self.hands to process
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.hands.process(img_rgb)

        if not result.multi_hand_landmarks: return

        self.hands_and_landmarks = {}

        for hand_id, hand_landmarks in enumerate(result.multi_hand_landmarks):
            # add array for each hand
            if not hand_id in self.hands_and_landmarks:
                self.hands_and_landmarks[hand_id] = []

            for id, lm in enumerate(hand_landmarks.landmark):
                height, width, _ = img.shape
                # find the coordinates of the lendmark's center
                cx, cy = int(lm.x * width), int(lm.y * height)

                # append coordinates and landmark id to given hand
                self.hands_and_landmarks[hand_id].append([id, cx, cy])

            if draw_landmarks:
                self.mp_draw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        self.hands_and_landmarks = {
            hand: np.array(self.hands_and_landmarks[hand]) for hand in self.hands_and_landmarks.keys()
        }

    def clear_hands_and_landmarks(self, img) -> None:
        self.hands_and_landmarks = {}
