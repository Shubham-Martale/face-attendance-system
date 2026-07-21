# 🧑‍💻 Face Recognition Based Automatic Attendance System

A complete, ready-to-run attendance system that recognizes student faces
through a webcam and automatically logs attendance into a database, with
a Streamlit-based admin dashboard for registration and reporting.

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| Front End | Streamlit (Admin Dashboard, Registration, Live Attendance, Reports) |
| Face Detection | MTCNN |
| Face Recognition | DeepFace (FaceNet embedding model) |
| Image Processing | OpenCV |
| Database | SQLite (swap-in MySQL by editing `database.py`) |
| Reports | pandas + openpyxl (CSV / Excel export) |

## 📁 Project Structure

```
face_attendance_system/
├── app.py                 # Streamlit front end (all pages/routes)
├── database.py             # SQLite schema + CRUD operations
├── face_utils.py           # Face detection & recognition (MTCNN + FaceNet)
├── requirements.txt
├── database/                # SQLite .db file generated here
├── known_faces/             # Registered student face images (student_id.jpg)
└── attendance_logs/          # (optional) exported reports land here
```

## ⚙️ Requirements

- Python 3.10+
- VS Code or PyCharm
- A webcam (for live capture via the browser)

## 🚀 Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The first time you run face recognition, DeepFace will automatically
download the FaceNet model weights (~90MB) into `~/.deepface/weights`.
This requires an internet connection on first run only.

## 🖥️ Using the App

1. **Register Student** — Enter Student ID, Name, Department, Email, then
   capture or upload a clear front-facing photo. The system detects the
   face with MTCNN and stores it in `known_faces/<student_id>.jpg`.
2. **Mark Attendance** — Open the camera, capture a frame. The system
   detects the face, compares it against all registered faces using
   FaceNet embeddings (cosine distance), and if a match is found below
   the threshold, logs "Present" with a timestamp (once per day per
   student).
3. **Attendance Report** — Filter by single day or date range, view in
   a table, and export to CSV or Excel.
4. **Manage Students** — View all registered students and delete any
   record (also removes their stored face image).
5. **Dashboard** — At-a-glance metrics: total students, present/absent
   today, and a 7-day attendance trend chart.

## 🔧 Configuration

In `face_utils.py`:
- `RECOGNITION_THRESHOLD` (default `0.40`) — lower = stricter matching.
  Tune this based on your environment/lighting if you see false
  matches or rejected genuine matches.
- `MODEL_NAME = "Facenet"` — can be swapped for `"Facenet512"`,
  `"ArcFace"`, or other DeepFace-supported models for higher accuracy
  at the cost of speed.

## 🗄️ Switching to MySQL

`database.py` currently uses `sqlite3`. To use MySQL instead, replace
the connection logic in `get_connection()` with `mysqlconnector` or
`PyMySQL`, and adjust the `CREATE TABLE` syntax (e.g. `AUTO_INCREMENT`
instead of `AUTOINCREMENT`). All other functions can remain unchanged
since they use standard parameterized SQL.

## 📝 Notes

- Each student can only be marked present once per calendar day
  (enforced by a `UNIQUE(student_id, date)` constraint).
- For best recognition accuracy: register with good, even lighting,
  a neutral expression, and the face filling a reasonable portion of
  the frame.
- This is a learning/demo-grade project — for production deployments,
  consider liveness detection (anti-spoofing) to prevent photo-based
  spoofing of the camera.
