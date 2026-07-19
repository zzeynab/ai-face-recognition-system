import numpy as np
from insightface.app import FaceAnalysis

from config.settings import DUPLICATE_THRESHOLD, RECOGNITION_THRESHOLD
from services.database_service import DatabaseService


class RecognitionService:
    """Face detection, embedding extraction, duplicate checks, and recognition."""

    def __init__(self):
        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)

        self.db = DatabaseService()
        self.known_faces = []
        self.load_database()

    def detect_faces(self, frame):
        return self.app.get(frame)

    def extract_embedding(self, frame):
        faces = self.detect_faces(frame)
        if not faces:
            return None
        return self.largest_face(faces).embedding

    @staticmethod
    def largest_face(faces):
        """Choose the most prominent detected face in a frame."""
        return max(
            faces,
            key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]),
        )

    @staticmethod
    def cosine_similarity(emb1, emb2):
        denominator = np.linalg.norm(emb1) * np.linalg.norm(emb2)
        if denominator == 0:
            return -1.0
        return float(np.dot(emb1, emb2) / denominator)

    def load_database(self):
        self.known_faces.clear()

        for row in self.db.get_all_embeddings():
            self.known_faces.append(
                {
                    "id": row["person_id"],
                    "name": f"{row['first_name']} {row['last_name']}",
                    "pose": row["pose"],
                    "embedding": row["embedding"],
                }
            )

        print(f"{len(self.known_faces)} embeddings loaded")

    def check_duplicate(self, embedding, threshold=DUPLICATE_THRESHOLD):
        """Find the best sample across all people for duplicate registration checks."""
        best_match = None
        best_score = -1.0

        for known_face in self.known_faces:
            score = self.cosine_similarity(embedding, known_face["embedding"])
            if score > best_score:
                best_score = score
                best_match = known_face

        if best_match is not None and best_score >= threshold:
            return {
                "duplicate": True,
                "person_id": best_match["id"],
                "name": best_match["name"],
                "score": best_score,
            }

        return {
            "duplicate": False,
            "person_id": None,
            "name": None,
            "score": best_score,
        }

    def recognize_face(self, current_embedding, threshold=RECOGNITION_THRESHOLD):
        """Pick the person with the best matching sample among all their samples."""
        best_by_person = {}

        for known_face in self.known_faces:
            score = self.cosine_similarity(current_embedding, known_face["embedding"])
            person_id = known_face["id"]

            if person_id not in best_by_person or score > best_by_person[person_id]["score"]:
                best_by_person[person_id] = {
                    "name": known_face["name"],
                    "score": score,
                }

        if not best_by_person:
            return "Unknown", -1.0

        best_result = max(best_by_person.values(), key=lambda result: result["score"])
        if best_result["score"] >= threshold:
            return best_result["name"], best_result["score"]

        return "Unknown", best_result["score"]
