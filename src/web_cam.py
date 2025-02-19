from gesture_recognition import GestureRecognizer, SequenceStage
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

detector = GestureRecognizer()

if __name__ == "__main__":
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        image = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                detector.process(hand_landmarks.landmark)
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
        stage : SequenceStage = detector.get_stage()
        color = (0, 255, 0)  # Default to green
        if stage == SequenceStage.SECONDGESTURE:
            color = (0, 255, 255)  # Yellow
        elif stage == SequenceStage.ALARM:
            color = (0, 0, 255)  # Red
            cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), color, 10)

        
        cv2.putText(image, f"Detected: {stage}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        
        cv2.imshow("Gesture Recognition", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
