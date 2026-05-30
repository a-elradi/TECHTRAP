import sys
import os

# Add src/ to path so all subpackages are importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import threading
import cv2
import tkinter as tk
import json
import time

from cvzone.HandTrackingModule import HandDetector
from utils.game_metrics import GameMetrics, plot_game_metrics
from reports.doctor_report import generate_doctor_pdf
from gui.gui import build_ui
import games.directkeys1 as dk1
import games.directkeys2 as dk2
import games.directkeys3 as dk3


game_running = False
current_game_thread = None
stop_requested = False


# =========================
#   DASHBOARD DATA SYSTEM
# =========================
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "sessions": 0,
            "total_time": 0,
            "games": {
                "game1": 0,
                "game2": 0,
                "game3": 0,
                "game4": 0
            }
        }, f, indent=4)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def log_game(game_name, duration):
    data = load_data()
    data["sessions"] += 1
    data["total_time"] += int(duration)
    data["games"][game_name] += 1
    save_data(data)


# =========================
#        GAME 1
# =========================
def game1():
    global game_running, stop_requested
    metrics = GameMetrics()
    print("Game 1 Selected")

    start_time = time.time()

    detector = HandDetector(detectionCon=0.5, maxHands=1)
    enter_key = dk1.enter_pressed
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        game_running = False
        return

    current_keys = set()

    while True:
        if stop_requested:
            break

        ok, frame = cap.read()
        if not ok:
            break

        hands, img = detector.findHands(frame)
        if hands:
            lm = hands[0]["lmList"]
            x, y = lm[8][0], lm[8][1]
            metrics.log_position(x, y)

        if hands and detector.fingersUp(hands[0]) == [0, 0, 0, 0, 0]:
            metrics.log_reaction(0.4)
            dk1.PressKey(enter_key)
            current_keys.add(enter_key)
        else:
            for k in current_keys:
                dk1.ReleaseKey(k)
            current_keys.clear()

        cv2.imshow("Game 1", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    for k in current_keys:
        dk1.ReleaseKey(k)

    results = metrics.compute_features()
    print("GAME METRICS:", results)

    from ai.mindspore_analysis import analyze_neuro_motor
    ai_result = analyze_neuro_motor(results)
    print("Neuro-Motor Score (AI):", ai_result)

    child_info = {
        "platform": "TECHTRAP",
        "child_name": "Player 1",
        "age": 7,
        "game_name": "Game 1",
        "session_id": f"G1_{int(time.time())}"
    }

    report_path = generate_doctor_pdf(
        child_info=child_info,
        game_metrics=results,
        ai_result=ai_result
    )
    print("Doctor Report Saved:", report_path)

    cap.release()
    cv2.destroyAllWindows()

    log_game("game1", time.time() - start_time)
    plot_game_metrics(results, child_name="Player 1")

    stop_requested = False
    game_running = False


def start_game1():
    global game_running
    if game_running:
        return
    game_running = True
    threading.Thread(target=game1, daemon=True).start()


# =========================
#        GAME 2
# =========================
def game2_race():
    global game_running, stop_requested

    print("Game 2 Selected - Hand Gas / Brake")

    metrics = GameMetrics()
    start_time = time.time()

    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.7, maxHands=1)

    GAS_KEY = dk2.right_pressed
    BRAKE_KEY = dk2.left_pressed

    gas_active = False
    reaction_start_time = time.time()

    while True:
        if stop_requested:
            break

        ok, img = cap.read()
        if not ok:
            break

        hands, img = detector.findHands(img, flipType=False)

        if hands:
            fingers = detector.fingersUp(hands[0])

            if fingers == [1, 1, 1, 1, 1]:
                if not gas_active:
                    reaction_time = time.time() - reaction_start_time
                    metrics.log_reaction(round(reaction_time, 3))
                    gas_active = True
                dk2.PressKey(GAS_KEY)
                dk2.ReleaseKey(BRAKE_KEY)

            elif fingers == [0, 0, 0, 0, 0]:
                dk2.ReleaseKey(GAS_KEY)
                dk2.PressKey(BRAKE_KEY)
                gas_active = False
                reaction_start_time = time.time()

            else:
                dk2.ReleaseKey(GAS_KEY)
                dk2.ReleaseKey(BRAKE_KEY)
                gas_active = False
                reaction_start_time = time.time()

        else:
            dk2.ReleaseKey(GAS_KEY)
            dk2.ReleaseKey(BRAKE_KEY)
            gas_active = False
            reaction_start_time = time.time()

        cv2.putText(
            img,
            "Open Hand = GAS | Fist = BRAKE | Q = Quit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("TECHTRAP - Racing Game", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    dk2.ReleaseKey(GAS_KEY)
    dk2.ReleaseKey(BRAKE_KEY)

    cap.release()
    cv2.destroyAllWindows()

    results = metrics.compute_features()
    print("GAME METRICS:", results)

    from ai.mindspore_analysis import analyze_neuro_motor
    ai_result = analyze_neuro_motor(results)

    child_info = {
        "platform": "TECHTRAP",
        "child_name": "Player 1",
        "age": 7,
        "session_id": f"RACE_{int(time.time())}"
    }

    report_path = generate_doctor_pdf(
        child_info=child_info,
        game_metrics=results,
        ai_result=ai_result
    )
    print("Doctor Report Saved:", report_path)

    log_game("game2", time.time() - start_time)

    stop_requested = False
    game_running = False


def start_game2():
    global game_running
    if game_running:
        return
    game_running = True
    threading.Thread(target=game2_race, daemon=True).start()


# =========================
#        GAME 3
# =========================
def game3():
    global game_running, stop_requested
    metrics = GameMetrics()
    print("Game 3 Selected")

    start_time = time.time()

    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    while True:
        if stop_requested:
            break

        ok, frame = cap.read()
        if not ok:
            break

        hands, img = detector.findHands(frame)
        if hands and detector.fingersUp(hands[0]) == [0, 0, 0, 0, 0]:
            dk3.PressKey(dk3.space_pressed)
        else:
            dk3.ReleaseKey(dk3.space_pressed)

        cv2.imshow("Game 3", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    dk3.ReleaseKey(dk3.space_pressed)

    results = metrics.compute_features()
    print("GAME METRICS:", results)

    from ai.mindspore_analysis import analyze_neuro_motor
    ai_result = analyze_neuro_motor(results)
    print("Neuro-Motor Score (AI):", ai_result)

    child_info = {
        "platform": "TECHTRAP",
        "child_name": "Player 1",
        "age": 7,
        "game_name": "Game 3",
        "session_id": f"G3_{int(time.time())}"
    }

    report_path = generate_doctor_pdf(
        child_info=child_info,
        game_metrics=results,
        ai_result=ai_result
    )
    print("Doctor Report Saved:", report_path)

    cap.release()
    cv2.destroyAllWindows()

    log_game("game3", time.time() - start_time)
    plot_game_metrics(results, child_name="Player 1")

    stop_requested = False
    game_running = False


def start_game3():
    global game_running
    if game_running:
        return
    game_running = True
    threading.Thread(target=game3, daemon=True).start()


# =========================
#        GAME 4
# =========================
def game4():
    global game_running, stop_requested
    metrics = GameMetrics()
    print("Game 4 Selected")

    start_time = time.time()

    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    while True:
        if stop_requested:
            break

        ok, img = cap.read()
        if not ok:
            break

        hands, img = detector.findHands(img)
        cv2.imshow("Pong", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    results = metrics.compute_features()
    print("GAME METRICS:", results)

    from ai.mindspore_analysis import analyze_neuro_motor
    ai_result = analyze_neuro_motor(results)
    print("Neuro-Motor Score (AI):", ai_result)

    child_info = {
        "platform": "TECHTRAP",
        "child_name": "Player 1",
        "age": 7,
        "game_name": "Game 4",
        "session_id": f"G4_{int(time.time())}"
    }

    report_path = generate_doctor_pdf(
        child_info=child_info,
        game_metrics=results,
        ai_result=ai_result
    )
    print("Doctor Report Saved:", report_path)

    cap.release()
    cv2.destroyAllWindows()

    log_game("game4", time.time() - start_time)
    plot_game_metrics(results, child_name="Player 1")

    stop_requested = False
    game_running = False


def start_game4():
    global game_running
    if game_running:
        return
    game_running = True
    threading.Thread(target=game4, daemon=True).start()


# =========================
#        STOP BUTTON
# =========================
def stop_game():
    global stop_requested, game_running
    stop_requested = True
    game_running = False
    print("STOP pressed")


# =========================
#        MAIN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    build_ui(
        root,
        on_game1=start_game1,
        on_game2=start_game2,
        on_game3=start_game3,
        on_game4=start_game4,
    )
    root.mainloop()
