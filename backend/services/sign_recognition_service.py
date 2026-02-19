from pathlib import Path
from typing import Optional
import sys

import cv2
import mediapipe as mp
import numpy as np
import torch
import torch.nn.functional as F

# Ensure legacy sign_recognition modules are importable.
ROOT_DIR = Path(__file__).resolve().parents[2]
LEGACY_SR_DIR = ROOT_DIR / "Sign_recognition" / "Sign Language Recognition"
if str(LEGACY_SR_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_SR_DIR))

from CNNModel import CNNModel  # type: ignore


class SignRecognitionService:
    """Service wrapper for sign recognition pipeline using CNN + MediaPipe landmarks."""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
            'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
            'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
        }
        self.idx_to_class = {v: k for k, v in self.classes.items()}

        self._model = self._load_model()

        self._hand_detector = None
        self._mediapipe_available = hasattr(mp, "solutions") and hasattr(mp, "__file__")
        if self._mediapipe_available:
            try:
                self._hand_detector = mp.solutions.hands.Hands(
                    static_image_mode=True,
                    min_detection_confidence=0.2,
                )
            except Exception:
                # If current mediapipe build lacks solutions (e.g., py3.14 wheels), fall back to landmarks input path.
                self._hand_detector = None
                self._mediapipe_available = False

    def _weights_path(self) -> Path:
        base = Path(__file__).resolve().parents[2]  # project root
        return base / "Sign_recognition" / "Sign Language Recognition" / "CNN_model_alphabet_SIBI.pth"

    def _load_model(self) -> torch.nn.Module:
        model = CNNModel()
        weights_path = self._weights_path()
        state = torch.load(weights_path, map_location=self.device)
        model.load_state_dict(state)
        model.to(self.device)
        model.eval()
        return model

    def _extract_landmarks(self, frame: object) -> Optional[np.ndarray]:
        """Return normalized landmark array of shape (63,) for the first detected hand.

        Accepts either:
        - dict with key 'landmarks' containing list/array length 63 (pre-computed pipeline)
        - numpy frame (BGR/RGB) if mediapipe solutions are available
        """
        # Pre-computed landmarks path (preferred when mediapipe solutions unavailable on this platform).
        if isinstance(frame, dict) and "landmarks" in frame:
            arr = np.array(frame["landmarks"], dtype=np.float32)
            if arr.shape[0] == 63:
                return arr
            return None

        if not self._mediapipe_available or self._hand_detector is None:
            return None

        if frame is None:
            return None
        if isinstance(frame, np.ndarray) and frame.ndim == 3 and frame.shape[2] == 3:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif isinstance(frame, np.ndarray):
            rgb = frame
        else:
            return None

        result = self._hand_detector.process(rgb)
        if not result or not getattr(result, "multi_hand_landmarks", None):
            return None

        hand_landmarks = result.multi_hand_landmarks[0]
        x_coords, y_coords, z_coords = [], [], []
        data = []

        for lm in hand_landmarks.landmark:
            x_coords.append(lm.x)
            y_coords.append(lm.y)
            z_coords.append(lm.z)

        if not x_coords:
            return None

        min_x, min_y, min_z = min(x_coords), min(y_coords), min(z_coords)

        for lm in hand_landmarks.landmark:
            data.extend([
                lm.x - min_x,
                lm.y - min_y,
                lm.z - min_z,
            ])

        return np.array(data, dtype=np.float32)

    def predict_from_frame(self, frame: object):
        """Run inference on a BGR frame or pre-computed landmarks and return top prediction with confidence."""
        landmarks = self._extract_landmarks(frame)
        if landmarks is None:
            return {"prediction": "NO_HAND_DETECTED", "confidence": 0.0, "detail": "Provide landmarks[63] or enable mediapipe solutions."}

        # Shape to (batch, channels, seq_len)
        tensor = torch.from_numpy(landmarks).to(self.device)
        tensor = tensor.view(1, 63, 1)

        with torch.no_grad():
            logits = self._model(tensor)
            probs = F.softmax(logits, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)

        pred_label = self.idx_to_class.get(int(pred_idx.item()), "UNKNOWN")
        return {"prediction": pred_label, "confidence": float(conf.item())}
