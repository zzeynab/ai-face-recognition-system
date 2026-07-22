# AI Face Recognition System

A desktop Face Recognition System developed using **Python**, **InsightFace**, **OpenCV**, **Tkinter**, and **SQLite**.

This project provides a complete face recognition solution with a graphical desktop interface for registering people, recognizing faces in real time, and managing stored face information. The system is designed using a modular architecture, making it easy to maintain, extend, and integrate with future features.

---

# Overview

The application allows users to register individuals by capturing their facial images from different head poses. During registration, facial embeddings are generated using the InsightFace deep learning framework and stored in a local SQLite database.

During live recognition, the system detects faces from the webcam, extracts embeddings, compares them with the stored embeddings using Cosine Similarity, and displays the identity of recognized people in real time.

The project follows a Service-Oriented Architecture where each module is responsible for a specific task such as database management, face recognition, camera handling, pose detection, registration, and graphical user interface.

---

# Features

- Face Registration
- Multi-Pose Face Registration
- Automatic Face Detection
- Face Embedding Extraction
- Duplicate Face Detection
- Live Face Recognition
- SQLite Database Storage
- Face Information Management
- Search Registered People
- Edit Person Information
- Delete Registered People
- Automatic Database Initialization
- Modern Tkinter Graphical Interface
- Persian Right-to-Left User Interface
- Modular Project Architecture
- Easy Project Maintenance
- Extensible Code Structure

---

# Technologies Used

- Python 3.11
- InsightFace
- OpenCV
- ONNX Runtime
- SQLite3
- Tkinter
- Pillow
- NumPy
- Arabic Reshaper
- Python Bidi

---

# Project Architecture

The project is organized into multiple independent modules.

```
ai-face-recognition-system/
│
├── assets/
│   └── fonts/
│
├── config/
│   └── settings.py
│
├── database/
│   ├── database.py
│   └── faces.db
│
├── gui/
│   ├── home_frame.py
│   ├── register_frame.py
│   ├── recognition_frame.py
│   ├── admin_frame.py
│   ├── main_window.py
│   └── theme.py
│
├── services/
│   ├── admin_service.py
│   ├── camera_service.py
│   ├── database_service.py
│   ├── pose_service.py
│   ├── recognition_service.py
│   └── registration_service.py
│
├── utils/
│   └── image_utils.py
│
├── config/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Project Workflow

The application follows the workflow below:

1. Launch the application.
2. Register a new person.
3. Capture facial images.
4. Detect the face.
5. Estimate head pose.
6. Generate face embedding.
7. Save information in SQLite database.
8. Start live recognition.
9. Detect faces from webcam.
10. Compare embeddings.
11. Display recognition results.
12. Manage registered people from the administration panel.

---

# Recognition Pipeline

```
Camera

↓

Face Detection

↓

Face Alignment

↓

Pose Estimation

↓

Embedding Extraction

↓

Embedding Comparison

↓

Identity Recognition

↓

Display Result
```

---

# Database Structure

The system stores all information inside a local SQLite database.

### Table: people

Stores personal information.

Fields:

- id
- first_name
- last_name
- register_time

### Table: embeddings

Stores facial embeddings.

Fields:

- id
- person_id
- pose
- embedding

Each person may have multiple embeddings corresponding to different head poses.

---

# Face Registration

The registration process consists of the following steps:

- Open webcam
- Detect face
- Verify image quality
- Detect head pose
- Extract embedding
- Check duplicate person
- Enter personal information
- Save person
- Save embeddings

Duplicate registration is prevented using Cosine Similarity before storing data.

---

# Live Face Recognition

During recognition the application continuously:

- Captures webcam frames
- Detects faces
- Extracts embeddings
- Compares embeddings
- Finds the closest registered person
- Displays name and similarity score

Unknown people are automatically labeled as **Unknown**.

---

# Administration Panel

The administration module provides:

- View registered people
- Search by first name
- Search by last name
- Edit personal information
- Delete registered people
- Automatic deletion of related embeddings

---

# Service-Oriented Design

Each service has a single responsibility.

### Camera Service

Responsible for:

- Opening webcam
- Capturing frames
- Saving images
- Releasing camera

---

### Recognition Service

Responsible for:

- Face detection
- Embedding extraction
- Cosine Similarity calculation
- Face recognition
- Loading embeddings

---

### Registration Service

Responsible for:

- Registering new people
- Validating user information
- Saving embeddings

---

### Database Service

Responsible for:

- Executing SQL queries
- CRUD operations
- Database transactions

---

### Pose Service

Responsible for:

- Detecting head pose
- Validating expected pose
- Controlling registration sequence

---

### Admin Service

Responsible for:

- Searching people
- Editing information
- Deleting people

---

# Installation

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install project dependencies.

```bash
pip install -r requirements.txt
```

Run the application.

```bash
python main.py
```

---

# System Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- Webcam
- Minimum 4 GB RAM
- Approximately 500 MB free disk space

---

# Future Improvements

Possible future developments include:

- Face Anti-Spoofing
- Mask Detection
- Attendance Management System
- User Authentication
- Multi-Camera Support
- GPU Acceleration
- Automatic Backup
- Cloud Database Support
- REST API
- Web Version
- Mobile Version
- Face Quality Assessment

---

# Author

**Zeynab Mokhtari**

Bachelor of Computer Engineering (Software)

Final Year Project

---

# License

This project has been developed for educational and research purposes as a Bachelor's Degree graduation project.