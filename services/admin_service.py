from services.database_service import DatabaseService


class AdminService:

    def __init__(self):
        self.database_service = DatabaseService()

    def get_people(self):
        return self.database_service.get_all_people()

    def search_people(self, text):
        return self.database_service.search_people(text)

    def update_person(self, person_id, first_name, last_name):
        first_name = first_name.strip()
        last_name = last_name.strip()

        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی نمی‌توانند خالی باشند.")

        updated = self.database_service.update_person(
            person_id,
            first_name,
            last_name,
        )

        if not updated:
            raise ValueError("شخص موردنظر پیدا نشد.")

    def delete_person(self, person_id):
        deleted = self.database_service.delete_person(person_id)

        if not deleted:
            raise ValueError("شخص موردنظر پیدا نشد.")