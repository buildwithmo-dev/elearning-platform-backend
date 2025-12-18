Here is the fused and finalized **README.md**. It combines your modular app architecture, Google OAuth integration, and the specific singular table names from your Supabase schema.

---

# Education Platform - Backend API

This is a multi-app Django backend integrated with **Supabase** (PostgreSQL) and **Google OAuth** on the supabase dashboard. It manages course lifecycles, real-time code execution via sandboxes, and live classroom integrations.

## 🏗️ Project Architecture

The backend is organized into three specialized Django applications:

1. **`api`**: The central hub for all business logic. It handles course delivery, curriculum fetching, and data processing between the frontend and Supabase.
2. **`users`**: Handles core identity management. It allows Django to manage custom user logic, fine-grained Authorization, and **Google OAuth** integration.
3. **`zoom_integration`**: A dedicated module for handling live online classes, managing meeting synchronization, and tracking attendance via the `attendance_record` table.

---

## 🔐 Security & Authentication

### Dual-Layer Authentication

* **Google OAuth**: Integrated via the `users` app for seamless student sign-on.
* **Django Auth**: Used for administrative controls and instructor-specific permissions.

### Database Security (RLS)

Security is enforced at the data layer using **Supabase Row Level Security (RLS)**. As seen in the schema, critical tables like `profiles`, `enrollment`, and `lesson` are protected to ensure:

* Users can only access their own profile data.
* Students can only view `lesson` content for courses they are active in via the `enrollment` table.
* Only authorized instructors can modify `course`, `module`, or `lesson` records.

---

## 📁 Database Schema (Singular)

The backend utilizes a strictly singular naming convention for database tables to ensure compatibility with PostgREST (Supabase) caching.

* **`course`**: Stores course metadata (title, instructor_id, price).
* **`module`**: Stores sectional groupings (title, course_id, order).
* **`lesson`**: Stores learning items (title, module_id, content_type, content_url).
* **`zoom_meetings`**: Metadata for live virtual sessions.
* **`attendance_record`**: Tracking for live session participation.

---

## 🚀 Key Features

* **Curriculum Engine**: Efficient fetching of multi-level structures for 160+ courses.
* **AI Sandbox**: An execution environment for Python/JS directly within the browser.
* **Seeding Tools**: Automation scripts included to generate 3,000+ lessons for testing.
* **Live Classes**: Real-time meeting management via Zoom.

---

## ⚙️ Getting Started

### 1. Prerequisites

* Python 3.14 or higher
* Supabase Project URL & Service Key
* Google Cloud Console credentials for OAuth

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/buildwithmo-dev/elearning-platform-backend.git
cd 

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_key
ZOOM_API_KEY=your_zoom_key

```

### 4. Running the Server

```bash
python manage.py migrate
python manage.py runserver

```

---

## 🧪 Seeding Data

To populate the database with the initial 160 courses and 3,200 lessons:

```bash
python3 seed_content.py

```
---

## 📡 API Endpoints (Core)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/courses/` | List all published courses |
| `GET` | `/api/courses/<id>/` | Fetch full curriculum (Lessons/Modules) |
| `POST` | `/api/courses/create/` | Instructor: Create a new course |
| `GET` | `/api/profiles/me/` | Fetch authenticated user profile |

---

## 🤝 Contributing

1. Fork the project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.
