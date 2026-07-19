"""Head-pose estimation used by guided multi-angle registration."""

from collections import deque

import numpy as np

from config.settings import (
    PITCH_DOWN_THRESHOLD,
    PITCH_UP_THRESHOLD,
    POSE_DETAILS,
    POSE_PITCH_DEGREES,
    POSE_YAW_DEGREES,
    REVERSE_YAW_DIRECTION,
    YAW_THRESHOLD,
)


class PoseService:
    """Classify an InsightFace face as front, left, right, up, or down."""

    def get_pose_info(self, face):
        """Return pose details, preferring model degrees and falling back to kps."""
        model_pose = self._read_model_pose(face)

        if model_pose is not None:
            pitch, yaw, roll = model_pose
            pose = self._classify_degree_pose(pitch, yaw)
            return {
                "pose": pose,
                "pitch": pitch,
                "yaw": yaw,
                "roll": roll,
                "source": "model_pose",
            }

        landmark_pose = self._read_landmark_pose(face)
        if landmark_pose is None:
            return {
                "pose": None,
                "pitch": None,
                "yaw": None,
                "roll": None,
                "source": "unavailable",
            }

        pitch_ratio, yaw_ratio = landmark_pose
        pose = self._classify_landmark_pose(pitch_ratio, yaw_ratio)
        return {
            "pose": pose,
            "pitch": pitch_ratio,
            "yaw": yaw_ratio,
            "roll": 0.0,
            "source": "landmarks",
        }

    def detect_pose(self, face):
        """Return only the classified pose name for compatibility with older code."""
        return self.get_pose_info(face)["pose"]

    def is_correct_pose(self, face, expected_pose):
        return self.detect_pose(face) == expected_pose

    def instruction_for(self, pose_name):
        """Get the Persian title and instruction for a target pose."""
        return POSE_DETAILS[pose_name]

    def _read_model_pose(self, face):
        """Read pitch/yaw/roll when the installed InsightFace model exposes them."""
        pose = getattr(face, "pose", None)
        if pose is None:
            return None

        try:
            values = np.asarray(pose, dtype=float).reshape(-1)
        except (TypeError, ValueError):
            return None

        if len(values) < 3 or not np.isfinite(values[:3]).all():
            return None

        return tuple(float(value) for value in values[:3])

    def _read_landmark_pose(self, face):
        """Estimate yaw and pitch ratios from InsightFace's five facial landmarks."""
        landmarks = getattr(face, "kps", None)
        if landmarks is None:
            return None

        try:
            points = np.asarray(landmarks, dtype=float)
        except (TypeError, ValueError):
            return None

        if points.shape[0] < 5 or points.shape[1] < 2:
            return None

        left_eye, right_eye, nose, left_mouth, right_mouth = points[:5, :2]
        eye_center = (left_eye + right_eye) / 2
        mouth_center = (left_mouth + right_mouth) / 2

        eye_distance = np.linalg.norm(right_eye - left_eye)
        face_height = mouth_center[1] - eye_center[1]

        if eye_distance < 1 or abs(face_height) < 1:
            return None

        yaw_ratio = (nose[0] - eye_center[0]) / eye_distance
        pitch_ratio = (nose[1] - eye_center[1]) / face_height

        return float(pitch_ratio), float(yaw_ratio)

    def _classify_degree_pose(self, pitch, yaw):
        yaw_value = -yaw if REVERSE_YAW_DIRECTION else yaw

        if yaw_value >= POSE_YAW_DEGREES:
            return "left"
        if yaw_value <= -POSE_YAW_DEGREES:
            return "right"
        if pitch >= POSE_PITCH_DEGREES:
            return "up"
        if pitch <= -POSE_PITCH_DEGREES:
            return "down"
        return "front"

    def _classify_landmark_pose(self, pitch_ratio, yaw_ratio):
        yaw_value = -yaw_ratio if REVERSE_YAW_DIRECTION else yaw_ratio

        if yaw_value >= YAW_THRESHOLD:
            return "left"
        if yaw_value <= -YAW_THRESHOLD:
            return "right"
        if pitch_ratio <= PITCH_UP_THRESHOLD:
            return "up"
        if pitch_ratio >= PITCH_DOWN_THRESHOLD:
            return "down"
        return "front"


class PoseStabilizer:
    """Require the same pose in consecutive frames before accepting a capture."""

    def __init__(self, required_frames=8):
        self.required_frames = required_frames
        self.history = deque(maxlen=required_frames)

    def reset(self):
        self.history.clear()

    def update(self, pose_name):
        """Return True only after the requested pose is stable long enough."""
        if pose_name is None:
            self.reset()
            return False

        self.history.append(pose_name)
        return (
            len(self.history) == self.required_frames
            and len(set(self.history)) == 1
        )

    def is_stable_for(self, pose_name):
        return (
            len(self.history) == self.required_frames
            and all(pose == pose_name for pose in self.history)
        )
