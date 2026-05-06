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


def compterNbrDoigt(fingers):
    return sum(fingers)


# Si mon petit doigt se lève je lance mappage
def mappage (hand_landmarks):
    return hand_landmarks.landmark[8].x,hand_landmarks.landmark[8].y



def click (fingers):
    if fingers[0] == 1:
        pyautogui.click()



# -------------------------
# VARIABLES
# -------------------------


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

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)


coinSup = None
coinInf = None
calibrated = False


prev_x, prev_y = pyautogui.position()



while True:
    ret, frame = cap.read()
    frame = cv.flip(frame, 1)


    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:


            fingers = fingers_up(hand_landmarks)

            if fingers[4] == 1 and coinSup is None:
                coinSup = mappage(hand_landmarks)
                print("Coin gauche : ", coinSup)
            if fingers[2] == 1 and coinInf is None:
                coinInf = mappage(hand_landmarks)


            if coinSup and coinInf:
                h, w, c = frame.shape

                x1 = int(coinSup[0] * w)
                y1 = int(coinSup[1] * h)
                x2 = int(coinInf[0] * w)
                y2 = int(coinInf[1] * h)

                cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                calibrated = True




            if calibrated :
                ix, iy = mappage(hand_landmarks);q

                # Normalisation dans la zone calibrée
                norm_x = (ix - coinSup[0]) / (coinInf[0] - coinSup[0])
                norm_x = 1 - norm_x
                norm_y = (iy - coinSup[1]) / (coinInf[1] - coinSup[1])

                # Clamp
                norm_x = max(0, min(1, norm_x))
                norm_y = max(0, min(1, norm_y))

                # Conversion écran
                mouse_x = norm_x * screen_w
                mouse_y = norm_y * screen_h

                # Smoothing
                smooth_x = prev_x + (mouse_x - prev_x) * 0.2
                smooth_y = prev_y + (mouse_y - prev_y) * 0.2

                pyautogui.moveTo(smooth_x, smooth_y)


                prev_x, prev_y = smooth_x, smooth_y
                click(fingers)

            print(compterNbrDoigt(fingers))

    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()



