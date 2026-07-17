import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import cv2

from services.database_service import DatabaseService
from services.recognition_service import RecognitionService


db = DatabaseService()
recognition = RecognitionService()


captured_embedding = None


# =====================================
# Capture Face
# =====================================

def capture_face():

    global captured_embedding

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



            result = recognition.check_duplicate(
                embedding
            )


            # -----------------------------
            # Duplicate Person
            # -----------------------------

            if result["duplicate"]:

                messagebox.showwarning(
                    "Duplicate Face",
                    f"Person already registered\n\n"
                    f"Name: {result['name']}\n"
                    f"Similarity: {result['score']:.2f}"
                )

                break



            # -----------------------------
            # New Person
            # -----------------------------

            captured_embedding = embedding


            show_register_fields()


            messagebox.showinfo(
                "New Person",
                "New face detected.\nEnter name and last name."
            )


            break



        if key == 27:
            break



    cap.release()
    cv2.destroyAllWindows()



# =====================================
# Show Name Fields
# =====================================

def show_register_fields():

    first_label.pack(
        pady=5
    )

    entry_first.pack()


    last_label.pack(
        pady=5
    )

    entry_last.pack()


    save_button.pack(
        pady=25
    )



# =====================================
# Save Person
# =====================================

def save_person():

    global captured_embedding


    if captured_embedding is None:

        messagebox.showerror(
            "Error",
            "Capture face first"
        )

        return



    first_name = entry_first.get().strip()
    last_name = entry_last.get().strip()



    if first_name == "" or last_name == "":

        messagebox.showerror(
            "Error",
            "Enter first name and last name"
        )

        return



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
        captured_embedding,
        "front"
    )


    recognition.load_database()



    messagebox.showinfo(
        "Success",
        f"{first_name} {last_name} registered successfully"
    )


    captured_embedding = None



    entry_first.delete(
        0,
        tk.END
    )

    entry_last.delete(
        0,
        tk.END
    )



# =====================================
# GUI
# =====================================

def main():

    global root

    global entry_first
    global entry_last

    global first_label
    global last_label

    global save_button



    root = tk.Tk()


    root.title(
        "Register New Face"
    )


    root.geometry(
        "400x300"
    )


    root.resizable(
        False,
        False
    )



    capture_button = tk.Button(
        root,
        text="Capture Face",
        width=25,
        height=2,
        command=capture_face
    )

    capture_button.pack(
        pady=30
    )



    # -----------------------------
    # Hidden Fields
    # -----------------------------

    first_label = tk.Label(
        root,
        text="First Name",
        font=("Arial", 11)
    )


    entry_first = tk.Entry(
        root,
        width=35
    )


    last_label = tk.Label(
        root,
        text="Last Name",
        font=("Arial", 11)
    )


    entry_last = tk.Entry(
        root,
        width=35
    )


    save_button = tk.Button(
        root,
        text="Save Person",
        width=25,
        height=2,
        command=save_person
    )



    root.mainloop()



if __name__ == "__main__":
    main()