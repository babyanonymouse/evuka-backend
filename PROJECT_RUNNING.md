# 🚀 How to Run Evuka LMS

This project consists of a **Django Backend** and a **React Frontend (AI Client)**.

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js & npm**

---

## 1. Backend Setup (Django)

Open a terminal in the root `evuka-backend` directory.

### Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Database & Migrations
# Note: We specifically migrate 'users' first to avoid dependency issues
python manage.py makemigrations users
python manage.py migrate

# 4. Create an Admin User (Optional, for accessing /admin)
python manage.py createsuperuser
```

### Running the Server

```bash
python manage.py runserver
```

The Backend API will be live at: **`http://127.0.0.1:8000/`**

---

## 2. Frontend Setup (AI Client)

Open a **new** terminal in the `evuka-backend/ai_client` directory.

### Installation

```bash
cd ai_client
npm install
```

### Running the Client

```bash
npm run dev -- --host
```

The Frontend will be live at: **`http://localhost:5173/`**

---

## 🧪 Testing the AI

1.  Ensure **BOTH** terminals are running (Backend & Frontend).
2.  Open **[http://localhost:5173/](http://localhost:5173/)** in your browser.
3.  **General Chat**: Type "What is Evuka?" to test the System Guide.
4.  **Course Tutor**: Enter a Course ID (e.g., `1`) in the top-right corner to chat with a specific course's context (requires existing courses in DB).

---

## 🔧 Troubleshooting

- **Migration Errors**: If you see "Dependency on app with no migrations: users", run:
  ```bash
  python manage.py makemigrations users
  python manage.py migrate
  ```
- **AI Not Responding**:
  - Check the backend terminal for errors.
  - Ensure `GEMINI_API_KEY` is set in your `.env` file.
  - Ensure the backend is running on port `8000`.