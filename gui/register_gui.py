import tkinter as tk
from tkinter import messagebox
import cv2
import sqlite3
import pickle
from datetime import datetime

from insightface.app import FaceAnalysis

app = FaceAnalysis()
app.prepare(ctx_id=0)

def capture_face():

    first_name = entry_first.get().strip()
    last_name = entry_last.get().strip()

    if first_name == "" or last_name == "":
        messagebox.showerror(
            "Error",
            "Please enter first name and last name"
        )
        return

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        cv2.putText(
            frame,
            "Press SPACE to Capture",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Register Face",
            frame
        )

        key = cv2.waitKey(1)

        if key == 32:

            faces = app.get(frame)

            if len(faces) == 0:

                messagebox.showerror(
                    "Error",
                    "No face detected"
                )

                continue

            face = faces[0]
            embedding = face.embedding

            register_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            conn = sqlite3.connect("database/faces.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO faces(
                    first_name,
                    last_name,
                    register_time,
                    embedding
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    register_time,
                    pickle.dumps(embedding)
                )
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"{first_name} {last_name} registered successfully"
            )

            break

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
root = tk.Tk()

root.title("Register New Face")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(
    root,
    text="First Name",
    font=("Arial", 11)
).pack(pady=(15, 5))

entry_first = tk.Entry(
    root,
    width=35
)

entry_first.pack()

tk.Label(
    root,
    text="Last Name",
    font=("Arial", 11)
).pack(pady=(15, 5))

entry_last = tk.Entry(
    root,
    width=35
)

entry_last.pack()

tk.Button(
    root,
    text="Capture Face",
    width=20,
    height=2,
    command=capture_face
).pack(pady=25)

root.mainloop()