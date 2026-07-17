import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import cv2

from services.database_service import DatabaseService
from services.recognition_service import RecognitionService
from services.camera_service import CameraService


class RegisterFrame(tk.Frame):

    def __init__(
        self,
        parent,
        controller
    ):

        super().__init__(parent)

        self.controller = controller

        self.db = DatabaseService()
        self.recognition = RecognitionService()
        self.camera = CameraService()

        self.captured_embedding = None

        self.build_ui()

    # =====================================
    # UI
    # =====================================

    def build_ui(self):

        title = tk.Label(
            self,
            text="ثبت چهره جدید",
            font=("Arial", 18, "bold")
        )

        title.pack(
            pady=20
        )


        self.capture_button = tk.Button(
            self,
            text="Capture Face",
            width=25,
            height=2,
            command=self.capture_face
        )

        self.capture_button.pack(
            pady=20
        )


        self.first_label = tk.Label(
            self,
            text="First Name",
            font=("Arial", 11)
        )


        self.entry_first = tk.Entry(
            self,
            width=35
        )


        self.last_label = tk.Label(
            self,
            text="Last Name",
            font=("Arial", 11)
        )


        self.entry_last = tk.Entry(
            self,
            width=35
        )


        self.save_button = tk.Button(
            self,
            text="Save Person",
            width=25,
            height=2,
            command=self.save_person
        )


        tk.Button(
            self,
            text="بازگشت",
            width=20,
            command=lambda: self.controller.show_frame(
                self.controller.home_frame
            )
        ).pack(
            pady=15
        )

    # =====================================
    # Capture Face
    # =====================================

    def capture_face(self):

        try:

            self.camera.open_camera()

        except Exception as e:

            messagebox.showerror(
                "Camera Error",
                str(e)
            )

            return


        while True:

            frame = self.camera.get_frame()

            if frame is None:
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

                embedding = self.recognition.extract_embedding(
                    frame
                )


                if embedding is None:

                    messagebox.showerror(
                        "Error",
                        "No face detected"
                    )

                    continue


                result = self.recognition.check_duplicate(
                    embedding
                )


                if result["duplicate"]:

                    messagebox.showwarning(
                        "Duplicate Face",
                        f"Person already registered\n\n"
                        f"Name: {result['name']}\n"
                        f"Similarity: {result['score']:.2f}"
                    )

                    break


                self.captured_embedding = embedding

                self.show_register_fields()

                messagebox.showinfo(
                    "New Person",
                    "New face detected.\nEnter name and last name."
                )

                break


            if key == 27:
                break


        self.camera.release()

        cv2.destroyAllWindows()
        
    # =====================================
    # Show Register Fields
    # =====================================

    def show_register_fields(self):

        self.first_label.pack(
            pady=5
        )

        self.entry_first.pack()

        self.last_label.pack(
            pady=5
        )

        self.entry_last.pack()

        self.save_button.pack(
            pady=25
        )

    # =====================================
    # Save Person
    # =====================================

    def save_person(self):

        if self.captured_embedding is None:

            messagebox.showerror(
                "Error",
                "Capture face first"
            )

            return

        first_name = self.entry_first.get().strip()
        last_name = self.entry_last.get().strip()

        if first_name == "" or last_name == "":

            messagebox.showerror(
                "Error",
                "Enter first name and last name"
            )

            return

        register_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        person_id = self.db.add_person(
            first_name,
            last_name,
            register_time
        )

        self.db.add_embedding(
            person_id,
            self.captured_embedding,
            "front"
        )

        self.recognition.load_database()

        messagebox.showinfo(
            "Success",
            f"{first_name} {last_name} registered successfully"
        )

        self.reset()