import tkinter as tk
from tkinter import messagebox

import cv2

from config.settings import (
    FACE_POSES,
    MIN_DETECTION_CONFIDENCE,
    MIN_FACE_SIZE,
    POSE_STABLE_FRAMES,
)
from gui.theme import COLORS, FONT_FAMILY
from gui.widgets import ElevatedCard, RtlProgressBar
from services.camera_service import CameraService
from services.pose_service import PoseService, PoseStabilizer
from services.recognition_service import RecognitionService
from services.registration_service import RegistrationService
from utils.image_utils import draw_persian_text


class RegisterFrame(tk.Frame):
    """Register five stable face poses in one continuous camera session."""

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
        self.session_finishing = False
        self.save_in_progress = False
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
        ).pack(pady=(15, 5))

        tk.Label(
            self,
            text="دوربین را یک‌بار باز کنید؛ پنج زاویه به‌صورت خودکار ثبت می‌شوند",
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["background"],
        ).pack(pady=(0, 5))

        self.card_shell = ElevatedCard(self)
        self.card_shell.pack(padx=25, pady=5)
        self.card = self.card_shell.content
        self.card.config(padx=38, pady=18)

        self.progress = RtlProgressBar(self.card, width=510, height=16)
        self.progress.pack(pady=(0, 8))

        self.progress_text = tk.Label(
            self.card,
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["primary"],
            bg=COLORS["surface"],
        )
        self.progress_text.pack(pady=(0, 10))

        pose_row = tk.Frame(self.card, bg=COLORS["surface"])
        pose_row.pack(fill=tk.X, pady=(0, 10))

        for pose in FACE_POSES:
            label = tk.Label(
                pose_row,
                text=pose["title"],
                font=(FONT_FAMILY, 10, "bold"),
                width=15,
                pady=4,
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
        self.target_label.pack(pady=(2, 5))

        self.instruction_label = tk.Label(
            self.card,
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
        )
        self.instruction_label.pack(pady=(0, 7))

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
            padx=30,
            pady=5,
            command=self.start_auto_capture,
        )
        self.capture_button.pack(pady=(0, 6))

        self.camera_hint = tk.Label(
            self.card,
            text="هر زاویه پس از ثابت‌ ماندن، بدون فشردن هیچ کلیدی ذخیره می‌شود",
            font=(FONT_FAMILY, 9),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
        )
        self.camera_hint.pack()

        self.name_form = tk.Frame(
            self.card,
            bg="#F8FAFC",
            highlightthickness=1,
            highlightbackground="#E2E8F0",
            padx=1,
            pady=18,
        )
        tk.Label(
            self.name_form,
            text="نام و نام خانوادگی را وارد کنید",
            font=(FONT_FAMILY, 9),
            fg=COLORS["muted"],
            bg="#F8FAFC",
            anchor="e",
        ).pack(fill=tk.X, pady=(1, 7))

        fields_row = tk.Frame(self.name_form, bg="#F8FAFC")
        fields_row.pack(fill=tk.X)
        first_field = tk.Frame(fields_row, bg="#F8FAFC")
        last_field = tk.Frame(fields_row, bg="#F8FAFC")
        first_field.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(0, 7))
        last_field.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(7, 0))

        self.first_label = tk.Label(
            first_field,
            text="نام",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["text"],
            bg="#F8FAFC",
            anchor="e",
        )
        self.first_label.pack(fill=tk.X, pady=(0, 5))
        self.entry_first = tk.Entry(
            first_field,
            font=(FONT_FAMILY, 12),
            justify="right",
            relief=tk.FLAT,
            bd=0,
            bg="white",
            fg=COLORS["text"],
            insertbackground=COLORS["primary"],
            highlightthickness=3,
            highlightbackground="#E8F0FA",
            highlightcolor="#BFDBFE",
        )
        self.entry_first.pack(fill=tk.X, ipady=3)

        self.last_label = tk.Label(
            last_field,
            text="نام خانوادگی",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLORS["text"],
            bg="#F8FAFC",
            anchor="e",
        )
        self.last_label.pack(fill=tk.X, pady=(0, 5))
        self.entry_last = tk.Entry(
            last_field,
            font=(FONT_FAMILY, 12),
            justify="right",
            relief=tk.FLAT,
            bd=0,
            bg="white",
            fg=COLORS["text"],
            insertbackground=COLORS["primary"],
            highlightthickness=3,
            highlightbackground="#E8F0FA",
            highlightcolor="#BFDBFE",
        )
        self.entry_last.pack(fill=tk.X, ipady=3)

        self.entry_first.bind("<FocusIn>", self._entry_focus_in)
        self.entry_last.bind("<FocusIn>", self._entry_focus_in)
        self.entry_first.bind("<FocusOut>", self._entry_focus_out)
        self.entry_last.bind("<FocusOut>", self._entry_focus_out)

        action_row = tk.Frame(self.name_form, bg="#F8FAFC")
        action_row.pack(pady=(20, 0))
        self.save_button = tk.Button(
            action_row,
            text="ذخیره اطلاعات",
            font=(FONT_FAMILY, 11, "bold"),
            bg="#16A34A",
            fg="white",
            activebackground="#15803D",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=3,
            command=self.save_new_person,
        )
        self.save_button.pack(side=tk.RIGHT, padx=(6, 0))
        self.cancel_button = tk.Button(
            action_row,
            text="لغو",
            font=(FONT_FAMILY, 11, "bold"),
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=3,
            command=self.cancel_registration,
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 6))

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
            pady=5,
            command=self.reset_session,
        ).pack(pady=(10, 3))

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
        ).pack(pady=(0, 10))

    def current_pose(self):
        return FACE_POSES[self.current_pose_index]

    def reset_session(self):
        self.camera.release()
        cv2.destroyAllWindows()

        self.pose_embeddings = {}
        self.current_pose_index = 0
        self.existing_person_id = None
        self.duplicate_checked = False
        self.session_finishing = False
        self.save_in_progress = False
        self.pose_stabilizer.reset()

        self.entry_first.delete(0, tk.END)
        self.entry_last.delete(0, tk.END)
        self.name_form.pack_forget()
        self.capture_button.config(state="normal")
        self.camera_hint.config(
            text="هر زاویه پس از ثابت‌ ماندن، بدون فشردن هیچ کلیدی ذخیره می‌شود.\n  برای لغو است Esc"
        )
        self.update_registration_ui()

    def update_registration_ui(self):
        completed_count = len(self.pose_embeddings)
        self.progress.set(completed_count, len(FACE_POSES))
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

    def start_auto_capture(self):
        """Keep the camera open and capture every requested pose automatically."""
        if self.session_finishing:
            return

        self.pose_stabilizer.reset()
        self.capture_button.config(state="disabled")

        try:
            self.camera.open_camera()
            cv2.namedWindow("Face Registration", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face Registration", 500, 400)
            cv2.moveWindow("Face Registration", 10, 10)
            try:
                cv2.setWindowProperty(
                    "Face Registration",
                    cv2.WND_PROP_TOPMOST,
                    1,
                )
            except cv2.error:
                pass
        except Exception as error:
            self.capture_button.config(state="normal")
            messagebox.showerror("خطای دوربین", str(error))
            return

        cancelled = False

        try:
            while self.current_pose_index < len(FACE_POSES):
                frame = self.camera.get_frame()
                if frame is None:
                    cancelled = True
                    messagebox.showerror("خطای دوربین", "دریافت تصویر از دوربین ناموفق بود.")
                    break

                expected_pose = self.current_pose()
                ready, status_text, color, face = self.validate_camera_frame(
                    self.recognition.detect_faces(frame),
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

                cv2.imshow("Face Registration", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    cancelled = True
                    break

                if not ready:
                    continue

                duplicate_action = self.handle_duplicate_if_needed(face.embedding)
                if duplicate_action == "cancel":
                    cancelled = True
                    break
                if duplicate_action == "restart":
                    continue

                self.pose_embeddings[expected_pose["name"]] = face.embedding.copy()
                self.current_pose_index += 1
                self.pose_stabilizer.reset()
                self.update_registration_ui()
                self.update_idletasks()

        finally:
            self.camera.release()
            cv2.destroyAllWindows()
            self.capture_button.config(state="normal")

        if cancelled:
            self.reset_session()
        elif self.current_pose_index == len(FACE_POSES) and not self.session_finishing:
            self.session_finishing = True
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

        detected_pose = self.pose_service.detect_pose(face)
        self.pose_stabilizer.update(detected_pose)

        if detected_pose != expected_pose:
            title = self.pose_service.instruction_for(detected_pose)["title"] if detected_pose else "نامشخص"
            return False, f"زاویهٔ فعلی: {title}", (0, 165, 255), face
        if not self.pose_stabilizer.is_stable_for(expected_pose):
            return False, "زاویه را ثابت نگه دارید...", (0, 255, 255), face

        return True, "زاویه درست است؛ ثبت خودکار انجام می‌شود.", (0, 255, 0), face

    def handle_duplicate_if_needed(self, embedding):
        if self.duplicate_checked:
            return "capture"

        self.duplicate_checked = True
        duplicate = self.recognition.check_duplicate(embedding)
        if not duplicate["duplicate"]:
            return "capture"

        should_add = messagebox.askyesno(
            "چهرهٔ تکراری",
            (
                f"این فرد قبلاً ثبت شده است.\n\n"
                f"نام: {duplicate['name']}\n"
                f"شباهت: {duplicate['score']:.2f}\n\n"
                "آیا پنج نمونهٔ جدید به این شخص افزوده شود؟"
            ),
        )
        if not should_add:
            return "cancel"

        self.existing_person_id = duplicate["person_id"]
        self.pose_embeddings.clear()
        self.current_pose_index = 0
        self.pose_stabilizer.reset()
        self.update_registration_ui()
        self.camera_hint.config(text=f"نمونه‌های جدید برای {duplicate['name']} ثبت می‌شوند.")
        return "restart"

    def finish_auto_capture(self):
        if self.existing_person_id is not None:
            self.save_samples_for_existing_person()
            return

        self.capture_button.config(state="disabled")
        self.name_form.pack(fill=tk.X, pady=(12, 0))
        self.entry_first.focus_set()

    def _entry_focus_in(self, event):
        """Use a soft blue focus ring instead of Tkinter's default dark border."""
        event.widget.config(highlightbackground="#BFDBFE", highlightcolor="#93C5FD")

    def _entry_focus_out(self, event):
        event.widget.config(highlightbackground="#E8F0FA")

    def cancel_registration(self):
        """Discard the captured samples and return the form to its initial state."""
        self.reset_session()

    def save_samples_for_existing_person(self):
        if self.save_in_progress:
            return

        self.save_in_progress = True
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
        except Exception as error:
            messagebox.showerror("خطای ذخیره", str(error))
            self.save_in_progress = False

    def save_new_person(self):
        if self.save_in_progress:
            return

        self.save_in_progress = True
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
        except Exception as error:
            messagebox.showerror("خطای ثبت", str(error))
            self.save_in_progress = False

    def reload_recognition_data(self):
        self.recognition.load_database()
        recognition_frame = self.controller.frames.get(self.controller.recognition_frame)
        if recognition_frame is not None:
            recognition_frame.recognition.load_database()

    def back_home(self):
        self.reset_session()
        self.controller.show_frame(self.controller.home_frame)
