from datetime import datetime

from config.settings import POSE_NAMES
from services.database_service import DatabaseService


class RegistrationService:
    """Business rules for registering a new face or adding samples to a person."""

    def __init__(self):
        self.database_service = DatabaseService()

    def validate_pose_embeddings(self, pose_embeddings):
        captured_poses = set(pose_embeddings)
        missing_poses = [pose for pose in POSE_NAMES if pose not in captured_poses]

        if missing_poses:
            raise ValueError("ثبت همهٔ پنج زاویهٔ چهره الزامی است.")

        if len(pose_embeddings) != len(POSE_NAMES):
            raise ValueError("یک یا چند زاویهٔ نامعتبر ثبت شده است.")

        if any(embedding is None for embedding in pose_embeddings.values()):
            raise ValueError("اطلاعات یکی از زاویه‌های چهره معتبر نیست.")

    def register_multi_pose_person(self, first_name, last_name, pose_embeddings):
        first_name = first_name.strip()
        last_name = last_name.strip()

        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی را وارد کنید.")

        self.validate_pose_embeddings(pose_embeddings)
        register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        person_id = self.database_service.create_person_with_embeddings(
            first_name=first_name,
            last_name=last_name,
            register_time=register_time,
            pose_embeddings=pose_embeddings,
        )

        return {
            "person_id": person_id,
            "first_name": first_name,
            "last_name": last_name,
            "register_time": register_time,
        }

    def add_multi_pose_samples(self, person_id, pose_embeddings):
        self.validate_pose_embeddings(pose_embeddings)

        person = self.database_service.get_person(person_id)
        if person is None:
            raise ValueError("شخص موردنظر در پایگاه داده پیدا نشد.")

        self.database_service.add_embeddings(person_id, pose_embeddings)
        return {
            "person_id": person[0],
            "first_name": person[1],
            "last_name": person[2],
        }

    def register_person(self, first_name, last_name, embedding, pose="front"):
        """Backward-compatible one-pose registration method."""
        first_name = first_name.strip()
        last_name = last_name.strip()

        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی را وارد کنید.")

        if embedding is None:
            raise ValueError("ابتدا چهره را ثبت کنید.")

        register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        person_id = self.database_service.add_person(
            first_name=first_name,
            last_name=last_name,
            register_time=register_time,
        )
        self.database_service.add_embedding(person_id, embedding, pose)

        return {
            "person_id": person_id,
            "first_name": first_name,
            "last_name": last_name,
        }
