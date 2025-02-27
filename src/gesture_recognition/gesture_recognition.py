from mediapipe.python.solutions import hands
from utilities import *
from enum import Enum
import numpy as np

# Constants
gesture_timeout = 10  # seconds

# Enums
class SequenceStage(Enum):
    IDLE = "Idle"
    INITIATED = "Initiated Sequence"
    SECONDGESTURE = "Second Gesture"
    ALARM = "Alarm Raised"


# Classes
class GestureRecognizer:
    def __init__(self, on_alarm=None):
        self.hands = hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.stop_watch = StopWatch()
        self.alarm_timer = StopWatch()
        self.sequence_started: bool = False
        self.thumb_in_palm: bool = False
        self.is_alarm_raised: bool = False
        self.on_alarm = on_alarm

    def process(self, landmarks) -> None:
        
        if self.is_alarm_raised:
            if self.alarm_timer.elapsed() >= 5:
                print("Alarm reset")
                self.is_alarm_raised = False
                self.alarm_timer.reset()

            return
        
        is_palm: bool = self._is_palm_open(landmarks)
        is_thumb_in_palm: bool = self._is_thumb_in_palm(landmarks)
        is_thumb_trapped: bool = self._is_thumb_trapped(landmarks)
        
        if not self.sequence_started:
            if is_palm:
                self.sequence_started = True
                self.stop_watch.start()
            return
        
        if self.stop_watch.elapsed() >= gesture_timeout:
            print("Gesture timeout")
            self.sequence_started = False
            self.thumb_in_palm = False
            self.stop_watch.reset()
        
        if is_thumb_in_palm:
            self.thumb_in_palm = True
            return
        
        if self.thumb_in_palm and is_thumb_trapped:
            self.is_alarm_raised = True
            self.sequence_started = False
            self.thumb_in_palm = False
            self.stop_watch.reset()
            self.alarm_timer.start()
            if self.on_alarm:
                self.on_alarm()
        
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
