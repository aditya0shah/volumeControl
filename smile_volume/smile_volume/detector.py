"""Smile detection using OpenCV Haar Cascades."""

import time
from typing import Optional

import cv2
import numpy as np


class SmileDetector:
    """Detects smiling from webcam using OpenCV Haar Cascades."""
    
    def __init__(
        self,
        camera_index: int = 0,
        ema_beta: float = 0.7,
        face_timeout_ms: int = 800,
    ):
        """
        Args:
            camera_index: Webcam device index
            ema_beta: Exponential moving average smoothing factor (0-1)
            face_timeout_ms: Time without face detection before treating as not smiling
        """
        self.camera_index = camera_index
        self.ema_beta = ema_beta
        self.face_timeout_ms = face_timeout_ms
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        self.smile_cascade: Optional[cv2.CascadeClassifier] = None
        self.smoothed_score: float = 0.0
        self.last_face_time: float = 0.0
    
    def start(self) -> None:
        """Initialize camera and OpenCV cascades."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_index}")
        
        # Optimize for performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Load Haar Cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_smile.xml'
        )
        
        self.last_face_time = time.time()
    
    def stop(self) -> None:
        """Release camera resources."""
        if self.cap:
            self.cap.release()
    
    def _compute_smile_score(self, face_roi: np.ndarray, face_w: int, face_h: int) -> float:
        """
        Compute smile score from face region of interest.
        
        Returns:
            Smile score (0.0 = not smiling, 1.0+ = smiling)
        """
        # Detect smiles in lower half of face
        lower_face = face_roi[face_h//2:, :]
        
        smiles = self.smile_cascade.detectMultiScale(
            lower_face,
            scaleFactor=1.8,
            minNeighbors=20,
            minSize=(25, 25),
        )
        
        if len(smiles) == 0:
            return 0.0
        
        # Score based on smile detection confidence and size
        # Larger and more centered smiles score higher
        max_score = 0.0
        for (sx, sy, sw, sh) in smiles:
            # Normalize by face size
            size_ratio = (sw * sh) / (face_w * face_h)
            
            # Check if smile is centered horizontally
            smile_center_x = sx + sw / 2
            face_center_x = face_w / 2
            center_offset = abs(smile_center_x - face_center_x) / face_w
            
            # Score: larger size + more centered = higher score
            score = size_ratio * 10.0 * (1.0 - center_offset)
            max_score = max(max_score, score)
        
        return max_score
    
    def get_smile_score(self) -> Optional[float]:
        """
        Capture frame and return current smile score.
        
        Returns:
            Smoothed smile score, or None if camera error or face timeout
        """
        if not self.cap or not self.face_cascade or not self.smile_cascade:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert to grayscale for Haar Cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100),
        )
        
        if len(faces) > 0:
            # Use first (largest) face
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            
            raw_score = self._compute_smile_score(face_roi, w, h)
            
            # Exponential moving average smoothing
            self.smoothed_score = (
                self.ema_beta * raw_score + (1 - self.ema_beta) * self.smoothed_score
            )
            
            self.last_face_time = time.time()
            return self.smoothed_score
        
        # No face detected - check timeout
        elapsed_ms = (time.time() - self.last_face_time) * 1000
        if elapsed_ms > self.face_timeout_ms:
            return None  # Treat as not smiling
        
        # Return last known score during brief face loss
        return self.smoothed_score
