import numpy as np
from insightface.app import FaceAnalysis

from services.database_service import DatabaseService


class RecognitionService:

    def __init__(self):

        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)

        self.db = DatabaseService()

        self.known_faces = []

        self.load_database()


    # ----------------------------------------
    # Detect Faces
    # ----------------------------------------

    def detect_faces(self, frame):

        return self.app.get(frame)


    # ----------------------------------------
    # Extract Embedding
    # ----------------------------------------

    def extract_embedding(self, frame):

        faces = self.detect_faces(frame)

        if len(faces) == 0:
            return None

        return faces[0].embedding


    # ----------------------------------------
    # Cosine Similarity
    # ----------------------------------------

    def cosine_similarity(
        self,
        emb1,
        emb2
    ):

        return np.dot(
            emb1,
            emb2
        ) / (
            np.linalg.norm(emb1)
            *
            np.linalg.norm(emb2)
        )


    # ----------------------------------------
    # Load Database
    # ----------------------------------------

    def load_database(self):

        self.known_faces.clear()

        rows = self.db.get_all_embeddings()

        for row in rows:

            # اگر خروجی دیتابیس Dictionary باشد
            if isinstance(row, dict):

                person_id = row["person_id"]
                first_name = row["first_name"]
                last_name = row["last_name"]
                pose = row["pose"]
                embedding = row["embedding"]


            # اگر خروجی دیتابیس Tuple باشد
            else:

                person_id = row[0]
                first_name = row[1]
                last_name = row[2]
                pose = row[3]
                embedding = row[4]


            self.known_faces.append({

                "id": person_id,

                "name":
                    f"{first_name} {last_name}",

                "pose":
                    pose,

                "embedding":
                    embedding
            })


        print(
            f"{len(self.known_faces)} embeddings loaded"
        )


    # ----------------------------------------
    # Check Duplicate Person
    # ----------------------------------------

    def check_duplicate(
        self,
        embedding,
        threshold=0.70
    ):

        best_name = None
        best_score = -1


        for person in self.known_faces:

            similarity = self.cosine_similarity(
                embedding,
                person["embedding"]
            )


            if similarity > best_score:

                best_score = similarity

                best_name = person["name"]


        if best_score >= threshold:

            return {

                "duplicate": True,

                "name": best_name,

                "score": best_score
            }


        return {

            "duplicate": False,

            "name": None,

            "score": best_score
        }


    # ----------------------------------------
    # Recognize Face
    # ----------------------------------------

    def recognize_face(
        self,
        current_embedding,
        threshold=0.60
    ):

        result = self.check_duplicate(
            current_embedding,
            threshold
        )


        if result["duplicate"]:

            return (
                result["name"],
                result["score"]
            )


        return (
            "Unknown",
            result["score"]
        )