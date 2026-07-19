import cv2
from insightface.app import FaceAnalysis

app = FaceAnalysis()
app.prepare(ctx_id=0)

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    faces = app.get(frame)

    if faces:

        face = faces[0]

        print("=" * 60)
        print("Pose:", face.pose)
        print("Type:", type(face.pose))

        break

    cv2.imshow("Test", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()