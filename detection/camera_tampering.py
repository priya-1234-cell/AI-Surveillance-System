import cv2
import time
import numpy as np


class CameraTamperDetector:
    def __init__(self, confirmation_seconds=3.0, cooldown_seconds=30.0):
        self.confirmation_seconds = confirmation_seconds
        self.cooldown_seconds = cooldown_seconds
        self.reference_brightness = None
        self.reference_sharpness = None
        self.reference_histogram = None
        self.startup_time = time.monotonic()
        self.pending_events = {}
        self.last_alert_time = {}
        self.baseline_samples = []

    def _measure(self, frame):
        small = cv2.resize(frame, (320, 180))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        histogram = cv2.calcHist([gray], [0], None, [32], [0, 256])
        histogram = cv2.normalize(histogram, histogram)
        return brightness, sharpness, histogram

    def update(self, frame):
        """Return confirmed events such as CAMERA COVERED."""
        now = time.monotonic()
        brightness, sharpness, histogram = self._measure(frame)

        if self.reference_brightness is None:
            self.baseline_samples.append((brightness, sharpness, histogram))
            if now - self.startup_time < 5.0:
                return []
            self.reference_brightness = float(np.median([x[0] for x in self.baseline_samples]))
            self.reference_sharpness = float(np.median([x[1] for x in self.baseline_samples]))
            self.reference_histogram = self.baseline_samples[-1][2]
            self.baseline_samples.clear()
            print("Camera baseline established.")
            return []

        candidates = []
        if self.reference_brightness > 20 and brightness < self.reference_brightness * 0.35:
            candidates.append("CAMERA COVERED")
        if self.reference_sharpness > 10 and sharpness < self.reference_sharpness * 0.25:
            candidates.append("CAMERA BLURRED")
        distance = cv2.compareHist(self.reference_histogram, histogram, cv2.HISTCMP_BHATTACHARYYA)
        if distance > 0.65:
            candidates.append("MAJOR VIEW CHANGE")

        events = []
        for event in candidates:
            if event not in self.pending_events:
                self.pending_events[event] = now
            elapsed = now - self.pending_events[event]
            last_alert = self.last_alert_time.get(event, 0)
            if elapsed >= self.confirmation_seconds and now - last_alert >= self.cooldown_seconds:
                events.append(event)
                self.last_alert_time[event] = now
        for event in list(self.pending_events):
            if event not in candidates:
                del self.pending_events[event]
        return events
