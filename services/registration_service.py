from datetime import datetime

from services.database_service import DatabaseService


class RegistrationService:

    def __init__(self):
        self.database_service = DatabaseService()

    def register_person(self, first_name, last_name, embedding, pose="front"):
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

        self.database_service.add_embedding(
            person_id=person_id,
            embedding=embedding,
            pose=pose,
        )

        return {
            "person_id": person_id,
            "first_name": first_name,
            "last_name": last_name,
        }