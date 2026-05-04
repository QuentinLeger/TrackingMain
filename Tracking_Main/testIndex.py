import numpy as np
import cv2 as cv
import mediapipe as mp
import pyautogui







def fingers_up(hand_landmarks):
    fingers = []

    # Raccourci
    lm = hand_landmarks.landmark

    # Pouce (cas spécial → on compare en X)
    if lm[4].x < lm[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Autres doigts (on compare en Y)
    tips = [8, 12, 16, 20]
    bases = [6, 10, 14, 18]

    for tip, base in zip(tips, bases):
        if lm[tip].y < lm[base].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers




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

cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    frame = cv.flip(frame, 1)
    if not ret:
        print("prblm")
        break

    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # --- Récupérer le bout de l’index
            h, w, c = frame.shape
            index_tip = hand_landmarks.landmark[8]
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)

            # --- Dessiner un point sur l’index
            cv.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

            # --- Convertir en coordonnées écran (CORRECT)
            mouse_x = int(index_tip.x * screen_w)
            mouse_y = int(index_tip.y * screen_h)

            pyautogui.moveTo(mouse_x, mouse_y)


            fingers = fingers_up(hand_landmarks)

            # Exemple : index levé seul
            if fingers == [0,1,0,0,0]:
                print("Index levé → action 1")

            # Exemple : index + majeur
            if fingers == [0,1,1,0,0]:
                print("Index + majeur → action 2")

            # Exemple : poing fermé
            if fingers == [0,0,0,0,0]:
                print("Poing → action 3")

            # Exemple : main ouverte
            if fingers == [1,1,1,1,1]:
                print("Main ouverte → action 4")

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()



