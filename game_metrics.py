#استخراج Neuro-Motor Features

import time

SESSION_DATA = {
    "start_time": None,
    "end_time": None,
    "actions": 0
}

def start_session():
    SESSION_DATA["start_time"] = time.time()
    SESSION_DATA["actions"] = 0

def register_action():
    SESSION_DATA["actions"] += 1

def end_session():
    SESSION_DATA["end_time"] = time.time()

def get_metrics():
    duration = SESSION_DATA["end_time"] - SESSION_DATA["start_time"]
    return {
        "duration_sec": round(duration, 2),
        "actions": SESSION_DATA["actions"],
        "actions_per_min": round(SESSION_DATA["actions"] / max(duration/60, 0.1), 2)
    }
# ===============================
# AI Neuro-Motor Metrics Collector
# ===============================

import time
import numpy as np

class GameMetrics:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.reaction_times = []
        self.positions = []
        self.errors = 0

    def log_reaction(self, reaction_time):
        self.reaction_times.append(reaction_time)

    def log_position(self, x, y):
        self.positions.append((x, y))

    def log_error(self):
        self.errors += 1

    def compute_features(self):
        duration = time.time() - self.start_time

        if len(self.reaction_times) > 0:
            avg_reaction = float(np.mean(self.reaction_times))
        else:
            avg_reaction = 0.0

        stability = 0.0
        if len(self.positions) > 1:
            diffs = np.diff(np.array(self.positions), axis=0)
            stability = float(np.mean(np.linalg.norm(diffs, axis=1)))

        return {
            "session_duration": round(duration, 2),
            "avg_reaction_time": round(avg_reaction, 3),
            "movement_stability": round(stability, 3),
            "error_count": int(self.errors),
        }
import matplotlib.pyplot as plt

def plot_game_metrics(metrics: dict, child_name="Child"):
    """
    يرسم رسومات بيانية لنتائج اللعب
    """
    labels = []
    values = []

    for k, v in metrics.items():
        labels.append(k.replace("_", " ").title())
        values.append(v)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)
    plt.title(f"TECHTRAP | Game Performance Report - {child_name}")
    plt.ylabel("Score")
    plt.xticks(rotation=20)

    # إظهار القيم فوق الأعمدة
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2,
                 yval + 0.01,
                 round(yval, 2),
                 ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

