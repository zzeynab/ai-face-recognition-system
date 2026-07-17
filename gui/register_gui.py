import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import cv2

from services.database_service import DatabaseService
from services.recognition_service import RecognitionService


db = DatabaseService()
recognition = RecognitionService()


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

            embedding = recognition.extract_embedding(frame)

            if embedding is None:

                messagebox.showerror(
                    "Error",
                    "No face detected"
                )

                continue

            register_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            person_id = db.add_person(
                first_name,
                last_name,
                register_time
            )

            db.add_embedding(
                person_id,
                embedding,
                "front"
            )

            messagebox.showinfo(
                "Success",
                f"{first_name} {last_name} registered successfully"
            )

            break

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def main():

    global root
    global entry_first
    global entry_last

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


if __name__ == "__main__":
    main()