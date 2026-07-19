import tkinter as tk
from tkinter import messagebox, ttk

import cv2

from config.settings import (
    FACE_POSES,
    MIN_DETECTION_CONFIDENCE,
    MIN_FACE_SIZE,
    POSE_STABLE_FRAMES,
)
from gui.theme import COLORS, FONT_FAMILY
from services.camera_service import CameraService
from services.pose_service import PoseService, PoseStabilizer
from services.recognition_service import RecognitionService
from services.registration_service import RegistrationService
from utils.image_utils import draw_persian_text


class RegisterFrame(tk.Frame):
    """Guided five-pose registration screen."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["background"])

        self.controller = controller
        self.camera = CameraService()
        self.recognition = RecognitionService()
        self.registration_service = RegistrationService()
        self.pose_service = PoseService()
        self.pose_stabilizer = PoseStabilizer(POSE_STABLE_FRAMES)

        self.pose_embeddings = {}
        self.current_pose_index = 0
        self.existing_person_id = None
        self.duplicate_checked = False
        self.pose_labels = {}

        self.build_ui()
        self.reset_session()

    def build_ui(self):
        tk.Label(
            self,
            text="ثبت هوشمند چهره",
            font=(FONT_FAMILY, 22, "bold"),
            fg=COLORS["text"],
            bg=COLORS["background"],
        ).pack(pady=(32, 5))

        tk.Label(
            self,
            text="برای دقت بهتر، پنج زاویهٔ چهره را طبق راهنما ثبت کنید.",
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["background"],
        ).pack(pady=(0, 18))

        self.card = tk.Frame(
            self,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=38,
            pady=24,
        )
        self.card.pack(padx=25, pady=5)

        self.progress = ttk.Progressbar(
            self.card,
            orient=tk.HORIZONTAL,
            length=510,
            mode="determinate",
            maximum=len(FACE_POSES),
        )
        self.progress.pack(pady=(0, 12))

        self.progress_text = tk.Label(
            self.card,
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["primary"],
            bg=COLORS["surface"],
        )
        self.progress_text.pack(pady=(0, 16))

        pose_row = tk.Frame(self.card, bg=COLORS["surface"])
        pose_row.pack(fill=tk.X, pady=(0, 18))

        for pose in FACE_POSES:
            label = tk.Label(
                pose_row,
                text=pose["title"],
                font=(FONT_FAMILY, 10, "bold"),
                width=9,
                pady=6,
                bg="#EAF0FA",
                fg=COLORS["muted"],
            )
            label.pack(side=tk.RIGHT, padx=3)
            self.pose_labels[pose["name"]] = label

        self.target_label = tk.Label(
            self.card,
            font=(FONT_FAMILY, 15, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
        )
        self.target_label.pack(pady=(4, 8))

        self.instruction_label = tk.Label(
            self.card,
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
        )
        self.instruction_label.pack(pady=(0, 20))

        self.capture_button = tk.Button(
            self.card,
            text="شروع ثبت خودکار پنج زاویه",
            font=(FONT_FAMILY, 11, "bold"),
            bg=COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=32,
            pady=10,
            command=self.start_auto_capture,
        )
        self.capture_button.pack(pady=(0, 10))

        self.camera_hint = tk.Label(
            self.card,
            text="دوربین را باز کنید و زاویه‌ها را به‌ترتیب تغییر دهید؛ ثبت خودکار است.",
            font=(FONT_FAMILY, 9),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
        )
        self.camera_hint.pack()

        self.name_form = tk.Frame(self.card, bg=COLORS["surface"])

        self.first_label = tk.Label(
            self.name_form,
            text="نام",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
            anchor="e",
        )
        self.entry_first = tk.Entry(
            self.name_form,
            width=38,
            font=(FONT_FAMILY, 11),
            justify="right",
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )

        self.last_label = tk.Label(
            self.name_form,
            text="نام خانوادگی",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
            anchor="e",
        )
        self.entry_last = tk.Entry(
            self.name_form,
            width=38,
            font=(FONT_FAMILY, 11),
            justify="right",
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )

        self.save_button = tk.Button(
            self.name_form,
            text="ذخیره پنج زاویه",
            font=(FONT_FAMILY, 11, "bold"),
            bg="#16A34A",
            fg="white",
            activebackground="#15803D",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self.save_new_person,
        )

        tk.Button(
            self,
            text="شروع مجدد",
            font=(FONT_FAMILY, 10),
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground="#EAF0FA",
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=7,
            command=self.reset_session,
        ).pack(pady=(14, 4))

        tk.Button(
            self,
            text="بازگشت به صفحهٔ اصلی",
            font=(FONT_FAMILY, 10),
            bg=COLORS["background"],
            fg=COLORS["muted"],
            activebackground="#EAF0FA",
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=7,
            command=self.back_home,
        ).pack(pady=(0, 20))

    def current_pose(self):
        return FACE_POSES[self.current_pose_index]

    def reset_session(self):
        self.camera.release()
        cv2.destroyAllWindows()

        self.pose_embeddings = {}
        self.current_pose_index = 0
        self.existing_person_id = None
        self.duplicate_checked = False
        self.pose_stabilizer.reset()

        self.entry_first.delete(0, tk.END)
        self.entry_last.delete(0, tk.END)
        self.name_form.pack_forget()
        self.capture_button.config(state="normal")
        self.camera_hint.config(
            text="دوربین را باز کنید و زاویه‌ها را به‌ترتیب تغییر دهید؛ ثبت خودکار است."
        )
        self.update_registration_ui()

    def update_registration_ui(self):
        completed_count = len(self.pose_embeddings)
        self.progress["value"] = completed_count
        self.progress_text.config(
            text=f"پیشرفت ثبت: {completed_count} از {len(FACE_POSES)} زاویه"
        )

        for pose in FACE_POSES:
            pose_name = pose["name"]
            label = self.pose_labels[pose_name]
            if pose_name in self.pose_embeddings:
                label.config(text=f"{pose['title']} ✓", bg="#DCFCE7", fg="#15803D")
            elif self.current_pose_index < len(FACE_POSES) and pose_name == self.current_pose()["name"]:
                label.config(text=pose["title"], bg="#DBEAFE", fg=COLORS["primary"])
            else:
                label.config(text=pose["title"], bg="#EAF0FA", fg=COLORS["muted"])

        if self.current_pose_index >= len(FACE_POSES):
            self.target_label.config(text="پنج زاویه با موفقیت دریافت شد.")
            self.instruction_label.config(text="نام و نام خانوادگی فرد جدید را وارد کنید.")
            return

        pose = self.current_pose()
        self.target_label.config(text=f"زاویهٔ موردنیاز: {pose['title']}")
        self.instruction_label.config(text=pose["instruction"])
        self.capture_button.config(text="شروع ثبت خودکار پنج زاویه")

    def start_auto_capture(self):
        self.pose_stabilizer.reset()
        self.capture_button.config(state="disabled")

        try:
            self.camera.open_camera()
        except Exception as error:
            self.capture_button.config(state="normal")
            messagebox.showerror("خطای دوربین", str(error))
            return

        cancelled = False

        try:
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    messagebox.showerror("خطای دوربین", "دریافت تصویر از دوربین ناموفق بود.")
                    cancelled = True
                    break

                expected_pose = self.current_pose()

                faces = self.recognition.detect_faces(frame)
                ready, status_text, color, face = self.validate_camera_frame(
                    faces,
                    expected_pose["name"],
                )

                frame = draw_persian_text(
                    frame,
                    f"هدف: {expected_pose['title']}",
                    (frame.shape[1] - 15, 18),
                    font_size=25,
                    color=(255, 255, 255),
                )
                frame = draw_persian_text(
                    frame,
                    status_text,
                    (frame.shape[1] - 15, 52),
                    font_size=21,
                    color=color,
                )

                cv2.imshow("Face Registration - ESC to cancel", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == 27:
                    cancelled = True
                    break

                if not ready:
                    continue

                if not self.handle_duplicate_if_needed(face.embedding):
                    cancelled = True
                    break

                self.pose_embeddings[expected_pose["name"]] = face.embedding.copy()
                self.current_pose_index += 1
                self.pose_stabilizer.reset()
                self.update_registration_ui()
                self.update_idletasks()

                if self.current_pose_index >= len(FACE_POSES):
                    break

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

        self.capture_button.config(state="normal")

        if cancelled:
            self.reset_session()
            return

        if self.current_pose_index >= len(FACE_POSES):
            self.finish_auto_capture()

    def validate_camera_frame(self, faces, expected_pose):
        if len(faces) == 0:
            self.pose_stabilizer.reset()
            return False, "چهره‌ای پیدا نشد.", (0, 0, 255), None

        if len(faces) > 1:
            self.pose_stabilizer.reset()
            return False, "فقط یک چهره باید در تصویر باشد.", (0, 0, 255), None

        face = faces[0]
        width = face.bbox[2] - face.bbox[0]
        height = face.bbox[3] - face.bbox[1]
        confidence = float(getattr(face, "det_score", 0.0))

        if width < MIN_FACE_SIZE or height < MIN_FACE_SIZE:
            self.pose_stabilizer.reset()
            return False, "کمی به دوربین نزدیک‌تر شوید.", (0, 165, 255), face

        if confidence < MIN_DETECTION_CONFIDENCE:
            self.pose_stabilizer.reset()
            return False, "نور و وضوح تصویر را بهتر کنید.", (0, 165, 255), face

        info = self.pose_service.get_pose_info(face)
        detected_pose = info["pose"]
        self.pose_stabilizer.update(detected_pose)

        if detected_pose != expected_pose:
            detected_title = (
                self.pose_service.instruction_for(detected_pose)["title"]
                if detected_pose
                else "نامشخص"
            )
            return False, f"زاویهٔ فعلی: {detected_title}", (0, 165, 255), face

        if not self.pose_stabilizer.is_stable_for(expected_pose):
            return False, "زاویه را ثابت نگه دارید...", (0, 255, 255), face

        return True, "زاویه درست است؛ ثبت خودکار انجام می‌شود.", (0, 255, 0), face

    def handle_duplicate_if_needed(self, embedding):
        if self.duplicate_checked:
            return True

        self.duplicate_checked = True
        duplicate = self.recognition.check_duplicate(embedding)

        if not duplicate["duplicate"]:
            return True

        add_samples = messagebox.askyesno(
            "چهرهٔ تکراری",
            (
                f"این فرد قبلاً ثبت شده است.\n\n"
                f"نام: {duplicate['name']}\n"
                f"شباهت: {duplicate['score']:.2f}\n\n"
                "آیا می‌خواهید پنج نمونهٔ جدید به این شخص اضافه شود؟"
            ),
        )

        if not add_samples:
            self.reset_session()
            return False

        self.existing_person_id = duplicate["person_id"]
        self.camera_hint.config(
            text=f"نمونه‌های جدید برای {duplicate['name']} ثبت می‌شوند."
        )
        return True

    def complete_current_pose(self):
        self.current_pose_index += 1
        self.update_registration_ui()

        if self.current_pose_index < len(FACE_POSES):
            return

        self.finish_auto_capture()

    def finish_auto_capture(self):
        """Continue with the correct save flow after all five angles are ready."""

        if self.existing_person_id is not None:
            self.save_samples_for_existing_person()
            return

        self.capture_button.config(state="disabled")
        self.name_form.pack(fill=tk.X, pady=(18, 0))
        self.first_label.pack(fill=tk.X, pady=(0, 4))
        self.entry_first.pack(fill=tk.X)
        self.last_label.pack(fill=tk.X, pady=(12, 4))
        self.entry_last.pack(fill=tk.X)
        self.save_button.pack(pady=(18, 0))
        self.entry_first.focus_set()

    def save_samples_for_existing_person(self):
        try:
            person = self.registration_service.add_multi_pose_samples(
                self.existing_person_id,
                self.pose_embeddings,
            )
            self.reload_recognition_data()
            messagebox.showinfo(
                "موفق",
                f"پنج نمونهٔ جدید برای {person['first_name']} {person['last_name']} ذخیره شد.",
            )
            self.reset_session()

        except ValueError as error:
            messagebox.showerror("خطا", str(error))

        except Exception as error:
            messagebox.showerror("خطای ذخیره", f"ذخیره نمونه‌ها ناموفق بود:\n{error}")

    def save_new_person(self):
        try:
            person = self.registration_service.register_multi_pose_person(
                first_name=self.entry_first.get(),
                last_name=self.entry_last.get(),
                pose_embeddings=self.pose_embeddings,
            )
            self.reload_recognition_data()
            messagebox.showinfo(
                "موفق",
                f"{person['first_name']} {person['last_name']} با پنج زاویه ثبت شد.",
            )
            self.reset_session()

        except ValueError as error:
            messagebox.showerror("خطا", str(error))

        except Exception as error:
            messagebox.showerror("خطای ثبت", f"ثبت اطلاعات ناموفق بود:\n{error}")

    def reload_recognition_data(self):
        """Refresh this screen and the live-recognition screen after a save."""
        self.recognition.load_database()

        recognition_frame = self.controller.frames.get(
            self.controller.recognition_frame
        )
        if recognition_frame is not None:
            recognition_frame.recognition.load_database()

    def back_home(self):
        self.reset_session()
        self.controller.show_frame(self.controller.home_frame)
