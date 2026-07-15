import cv2
import sqlite3
import pickle
import numpy as np

from insightface.app import FaceAnalysis

# ---------------------------
# فارسی‌سازی متن
# ---------------------------
import arabic_reshaper
from bidi.algorithm import get_display

from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# تنظیمات
# ---------------------------
THRESHOLD = 0.60


# ---------------------------
# تابع نمایش متن (فارسی + رنگ)
# ---------------------------
def put_farsi_text(img, text, position, font_size=32, color=(0, 255, 0)):

    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    font = ImageFont.truetype("assets/fonts/arial.ttf", 28)

    draw.text(position, bidi_text, font=font, fill=color)

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


# ---------------------------
# بارگذاری دیتابیس
# ---------------------------
conn = sqlite3.connect("database/faces.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT first_name, last_name, embedding
    FROM faces
""")

records = cursor.fetchall()
conn.close()

known_faces = []

for first_name, last_name, emb_blob in records:
    full_name = f"{first_name} {last_name}"
    embedding = pickle.loads(emb_blob)
    known_faces.append((full_name, embedding))

print(f"{len(known_faces)} faces loaded")


# ---------------------------
# بارگذاری مدل
# ---------------------------
app = FaceAnalysis()
app.prepare(ctx_id=0)


# ---------------------------
# دوربین
# ---------------------------
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)

    for face in faces:

        x1, y1, x2, y2 = map(int, face.bbox)
        current_embedding = face.embedding

        best_name = "Unknown"
        best_score = -1

        # ---------------------------
        # مقایسه چهره‌ها
        # ---------------------------
        for name, stored_embedding in known_faces:

            similarity = np.dot(
                current_embedding,
                stored_embedding
            ) / (
                np.linalg.norm(current_embedding) *
                np.linalg.norm(stored_embedding)
            )

            if similarity > best_score:
                best_score = similarity
                best_name = name

        # ---------------------------
        # تصمیم نهایی
        # ---------------------------
        if best_score < THRESHOLD:
            best_name = "ناشناس"
            box_color = (0, 0, 255)   # قرمز
            text_color = (0, 0, 255)
        else:
            box_color = (0, 255, 0)   # سبز
            text_color = (0, 255, 0)

        label = f"{best_name} ({best_score:.2f})"

        # ---------------------------
        # رسم باکس
        # ---------------------------
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )

        # ---------------------------
        # متن روی تصویر (فارسی)
        # ---------------------------
        frame = put_farsi_text(
            frame,
            label,
            (x1, y1 - 40),
            28,
            text_color
        )

    # نمایش خروجی
    cv2.imshow("Face Recognition System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()