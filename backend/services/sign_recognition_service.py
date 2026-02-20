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

        self.mp_hands = None
        self.hands = None
        mp_version = getattr(mp, "__version__", "unknown")
        mp_file = getattr(mp, "__file__", "unknown")
        has_solutions = hasattr(mp, "solutions")
        print(f"[init] mediapipe version={mp_version}, file={mp_file}, has_solutions={has_solutions}")

        self._mediapipe_available = True  # attempt and downgrade on failure
        try:
            self.mp_hands = mp.solutions.hands if has_solutions else None
            if self.mp_hands is None:
                raise RuntimeError("mediapipe.solutions.hands not present")

            # static_image_mode=True because we submit one-off stills from the webcam button.
            self.hands = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                model_complexity=1,
                min_detection_confidence=0.2,
                min_tracking_confidence=0.2,
            )
            print("[init] hands created")
        except Exception as exc:
            print(f"[init] failed to create hands: {exc}")
            self.hands = None
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

        if not self._mediapipe_available or self.hands is None:
            print(f"[mediapipe] unavailable or hands None: available={self._mediapipe_available}, hands={self.hands}")
            return None

        if frame is None:
            return None
        if isinstance(frame, np.ndarray) and frame.ndim == 3 and frame.shape[2] == 3:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif isinstance(frame, np.ndarray):
            rgb = frame
        else:
            return None

        rgb = np.ascontiguousarray(rgb)
        rgb.flags.writeable = False

        print(
            f"[mediapipe] frame shape: {frame.shape if hasattr(frame, 'shape') else 'unknown'}, "
            f"dtype={frame.dtype if hasattr(frame, 'dtype') else 'na'}"
        )

        results = self.hands.process(rgb)
        print("results:", results)
        mhl = results.multi_hand_landmarks if results else None
        print("multi_hand_landmarks:", mhl)

        if not mhl:
            return None

        hand_landmarks = mhl[0]
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
        """Run MediaPipe hand detection then classify landmarks with the CNN model."""
        print(f"[predict] frame type: {type(frame)}")

        if frame is None:
            return {"prediction": "NO_HAND_DETECTED", "confidence": 0.0}

        precomputed_landmarks = None
        if isinstance(frame, dict) and "landmarks" in frame:
            print("[predict] received precomputed landmarks")
            precomputed_landmarks = np.array(frame["landmarks"], dtype=np.float32)

        if not isinstance(frame, np.ndarray) and precomputed_landmarks is None:
            return {"prediction": "NO_HAND_DETECTED", "confidence": 0.0}

        if isinstance(frame, np.ndarray):
            print(f"[predict] frame shape: {frame.shape if hasattr(frame, 'shape') else 'unknown'}")

        landmarks = precomputed_landmarks if precomputed_landmarks is not None else self._extract_landmarks(frame)

        if landmarks is None:
            return {"prediction": "NO_HAND_DETECTED", "confidence": 0.0}

        tensor = torch.tensor(landmarks, dtype=torch.float32, device=self.device).view(1, 63, 1)

        with torch.no_grad():
            logits = self._model(tensor)
            probs = F.softmax(logits, dim=1)
            confidence, pred_idx = torch.max(probs, dim=1)

        pred_class = self.idx_to_class.get(pred_idx.item(), "?")
        return {"prediction": pred_class, "confidence": float(confidence.item())}
