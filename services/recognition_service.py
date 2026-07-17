import numpy as np
from insightface.app import FaceAnalysis

from services.database_service import DatabaseService


class RecognitionService:

    def __init__(self):

        self.db = DatabaseService()

        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)

        self.known_faces = []

        self.reload_database()

    # ==========================================
    # Database
    # ==========================================

    def reload_database(self):

        self.known_faces = self.db.get_all_embeddings()

    # ==========================================
    # Face Detection
    # ==========================================

    def detect_faces(self, frame):

        return self.app.get(frame)

    # ==========================================
    # Get First Face
    # ==========================================

    def get_first_face(self, frame):

        faces = self.detect_faces(frame)

        if len(faces) == 0:
            return None

        return faces[0]

    # ==========================================
    # Extract Embedding
    # ==========================================

    def extract_embedding(self, frame):

        face = self.get_first_face(frame)

        if face is None:
            return None

        return face.embedding

    # ==========================================
    # Cosine Similarity
    # ==========================================

    @staticmethod
    def cosine_similarity(emb1, emb2):

        denominator = (
            np.linalg.norm(emb1)
            * np.linalg.norm(emb2)
        )

        if denominator == 0:
            return -1

        return float(
            np.dot(emb1, emb2) / denominator
        )

    # ==========================================
    # Recognition
    # ==========================================

    def recognize_face(
        self,
        embedding,
        threshold=0.60
    ):

        if embedding is None:

            return {
                "name": "Unknown",
                "score": 0,
                "person_id": None,
                "pose": None
            }

        best_match = None
        best_score = -1

        for person in self.known_faces:

            score = self.cosine_similarity(
                embedding,
                person["embedding"]
            )

            if score > best_score:

                best_score = score
                best_match = person

        if best_match is None or best_score < threshold:

            return {
                "name": "Unknown",
                "score": best_score,
                "person_id": None,
                "pose": None
            }

        return {

            "name": f'{best_match["first_name"]} {best_match["last_name"]}',

            "score": best_score,

            "person_id": best_match["person_id"],

            "pose": best_match["pose"]

        }

    # ==========================================
    # Register New Face
    # ==========================================

    def register_face(
        self,
        person_id,
        embedding,
        pose="front"
    ):

        self.db.add_embedding(
            person_id,
            embedding,
            pose
        )

        self.reload_database()