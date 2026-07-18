import tkinter as tk
from tkinter import messagebox

import cv2

from services.camera_service import CameraService
from services.recognition_service import RecognitionService
from services.registration_service import RegistrationService


class RegisterFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.camera = CameraService()
        self.recognition = RecognitionService()
        self.registration_service = RegistrationService()

        self.captured_embedding = None

        self.build_ui()

    # =====================================
    # UI
    # =====================================

    def build_ui(self):
        tk.Label(
            self,
            text="ثبت چهره جدید",
            font=("Arial", 18, "bold"),
        ).pack(pady=20)

        self.capture_button = tk.Button(
            self,
            text="گرفتن تصویر چهره",
            width=25,
            height=2,
            command=self.capture_face,
        )
        self.capture_button.pack(pady=20)

        self.first_label = tk.Label(
            self,
            text="نام",
            font=("Arial", 11),
        )

        self.entry_first = tk.Entry(
            self,
            width=35,
        )

        self.last_label = tk.Label(
            self,
            text="نام خانوادگی",
            font=("Arial", 11),
        )

        self.entry_last = tk.Entry(
            self,
            width=35,
        )

        self.save_button = tk.Button(
            self,
            text="ذخیره شخص",
            width=25,
            height=2,
            command=self.save_person,
        )

        tk.Button(
            self,
            text="بازگشت",
            width=20,
            command=self.back_home,
        ).pack(pady=15)

    # =====================================
    # Capture face
    # =====================================

    def capture_face(self):
        try:
            self.camera.open_camera()

        except Exception as error:
            messagebox.showerror("خطای دوربین", str(error))
            return

        try:
            while True:
                frame = self.camera.get_frame()

                if frame is None:
                    messagebox.showerror(
                        "خطای دوربین",
                        "دریافت تصویر از دوربین ناموفق بود.",
                    )
                    break

                cv2.putText(
                    frame,
                    "Press SPACE to capture | ESC to cancel",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

                cv2.imshow("Register Face", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == 27:
                    break

                if key != 32:
                    continue

                embedding = self.recognition.extract_embedding(frame)

                if embedding is None:
                    messagebox.showerror(
                        "خطا",
                        "چهره‌ای در تصویر تشخیص داده نشد. دوباره تلاش کنید.",
                    )
                    continue

                result = self.recognition.check_duplicate(embedding)

                if result["duplicate"]:
                    messagebox.showwarning(
                        "چهره تکراری",
                        (
                            "این شخص قبلاً ثبت شده است.\n\n"
                            f"نام: {result['name']}\n"
                            f"شباهت: {result['score']:.2f}"
                        ),
                    )
                    break

                self.captured_embedding = embedding
                self.show_register_fields()

                messagebox.showinfo(
                    "چهره جدید",
                    "چهره با موفقیت ثبت موقت شد.\n"
                    "اکنون نام و نام خانوادگی را وارد کنید.",
                )
                break

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

    # =====================================
    # Show form fields
    # =====================================

    def show_register_fields(self):
        self.first_label.pack(pady=5)
        self.entry_first.pack()

        self.last_label.pack(pady=5)
        self.entry_last.pack()

        self.save_button.pack(pady=25)

        self.entry_first.focus_set()

    # =====================================
    # Save person
    # =====================================

    def save_person(self):
        try:
            person = self.registration_service.register_person(
                first_name=self.entry_first.get(),
                last_name=self.entry_last.get(),
                embedding=self.captured_embedding,
                pose="front",
            )

            self.recognition.load_database()

            messagebox.showinfo(
                "موفق",
                (
                    f"{person['first_name']} "
                    f"{person['last_name']} با موفقیت ثبت شد."
                ),
            )

            self.reset()

        except ValueError as error:
            messagebox.showerror("خطا", str(error))

        except Exception as error:
            messagebox.showerror(
                "خطای ثبت",
                f"ثبت اطلاعات با خطا مواجه شد:\n{error}",
            )

    # =====================================
    # Reset form
    # =====================================

    def reset(self):
        self.captured_embedding = None

        self.entry_first.delete(0, tk.END)
        self.entry_last.delete(0, tk.END)

        self.first_label.pack_forget()
        self.entry_first.pack_forget()

        self.last_label.pack_forget()
        self.entry_last.pack_forget()

        self.save_button.pack_forget()

    # =====================================
    # Back
    # =====================================

    def back_home(self):
        self.reset()

        self.controller.show_frame(
            self.controller.home_frame
        )