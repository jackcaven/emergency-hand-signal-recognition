from mediapipe.python.solutions import hands
from utilities import *
from enum import Enum
import numpy as np

# Constants
gesture_timeout = 10  # seconds
alarm_timeout = 5  # seconds


# Enums
class SequenceStage(Enum):
    IDLE = "Idle"
    INITIATED = "Initiated Sequence"
    SECONDGESTURE = "Second Gesture"
    ALARM = "Alarm Raised"


# Classes
class GestureRecognizer:
    def __init__(self):
        self.hands = hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.stop_watch = StopWatch()
        self.sequence_started: bool = False
        self.thumb_in_palm: bool = False
        self.is_alarm_raised: bool = False

    def process(self, landmarks) -> None:
        if self.is_alarm_raised and self.stop_watch.elapsed() <= alarm_timeout:
            return
        
        if self.is_alarm_raised:
            self.is_alarm_raised = False
            self.stop_watch.reset()

        if self._is_palm_open(landmarks) and not self.is_alarm_raised:
            self.sequence_started = True
            self.stop_watch.start()
            self.thumb_in_palm = False
            self.is_alarm_raised = False
        else:
            self.is_alarm_raised = False
            self.stop_watch.reset()

        if not self.sequence_started or self.stop_watch.elapsed() > gesture_timeout:
            self.sequence_started = False
            self.stop_watch.reset()
            return

        if not self.thumb_in_palm and self._is_thumb_in_palm(landmarks):
            self.thumb_in_palm = True
            return

        if not self.is_alarm_raised and self._is_thumb_trapped(landmarks):
            self.is_alarm_raised = True
            return

    def get_stage(self) -> SequenceStage:
        if self.is_alarm_raised:
            return SequenceStage.ALARM
        elif self.thumb_in_palm:
            return SequenceStage.SECONDGESTURE
        elif self.sequence_started:
            return SequenceStage.INITIATED
        else:
            return SequenceStage.IDLE

    def _is_palm_open(self, landmarks):
        points = np.array([[lm.x, lm.y] for lm in landmarks])

        # All fingers should be extended (higher y-coordinates than their lower joints)
        fingers_extended = all(points[i][1] < points[i - 2][1] for i in [8, 12, 16, 20])

        return fingers_extended

    def _is_thumb_in_palm(self, landmarks):
        points = np.array([[lm.x, lm.y] for lm in landmarks])
        return points[4][0] < points[3][0]  # Thumb moving toward palm

    def _is_thumb_trapped(self, landmarks):
        points = np.array([[lm.x, lm.y] for lm in landmarks])
        return all(
            points[i][1] > points[i - 2][1] for i in [8, 12, 16, 20]
        )  # Fingers bending down
