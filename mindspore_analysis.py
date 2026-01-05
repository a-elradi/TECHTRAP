# ============================================
# TECHTRAP - MindSpore Neuro-Motor AI Analysis
# ============================================

import mindspore as ms
import mindspore.nn as nn
import mindspore.ops as ops
from mindspore import Tensor
import numpy as np

# ============================================
# AI MODEL: Neuro-Motor Assessment Network
# ============================================

class NeuroMotorNet(nn.Cell):
    """
    Neural Network for Neuro-Motor Assessment
    Input  : Game Metrics (4 features)
    Output : Neuro-Motor Score (0 → 1)
    """
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Dense(4, 16)
        self.fc2 = nn.Dense(16, 8)
        self.fc3 = nn.Dense(8, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def construct(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x


# ============================================
# AI Inference Function (MAIN ENTRY POINT)
# ============================================

def analyze_neuro_motor(metrics: dict):
    """
    TECHTRAP AI-Powered Neuro-Motor Assessment

    Input:
        metrics (dict) from game_metrics.compute_features()

    Expected Keys:
        - avg_speed
        - stability
        - reaction_time
        - error_rate

    Output:
        dict:
            - neuro_motor_score (0–100)
            - risk_level
    """

    # Initialize model
    model = NeuroMotorNet()

    # Ensure fixed feature order
    features = [
        float(metrics.get("avg_speed", 0)),
        float(metrics.get("stability", 0)),
        float(metrics.get("reaction_time", 0)),
        float(metrics.get("error_rate", 0)),
    ]

    # Convert to MindSpore Tensor
    x = Tensor(np.array([features]), ms.float32)

    # AI Inference
    score = model(x)
    score_percent = float(score.asnumpy()[0][0]) * 100

    # Risk Level Classification
    if score_percent >= 80:
        risk = "Normal"
    elif score_percent >= 55:
        risk = "Mild Delay"
    else:
        risk = "Needs Attention"

    return {
        "neuro_motor_score": round(score_percent, 2),
        "risk_level": risk
    }


# ============================================
# END OF FILE
# ============================================
