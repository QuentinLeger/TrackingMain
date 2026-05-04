import numpy as np
import cv2 as cv
import mediapipe as mp
import pyautogui

screen_w, screen_h = pyautogui.size()
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("prblm")
        break

    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # 🔥 DESSIN DES POINTS + LIGNES
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # 🔥 AFFICHAGE DU NUMÉRO DE CHAQUE POINT
            h, w, c = frame.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv.putText(frame, str(id), (cx, cy),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5,
                           (0, 255, 0), 2)

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
