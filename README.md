# Evuka – Practical E‑Learning Reimagined

Evuka bridges the gap between theoretical online coursework and practical, community‑driven education by unifying **Live Events**, **Quizzes**, **Assignments**, and **Organizational Portals** into a single cohesive platform.

---

## 🎯 Platform Philosophy: Practical & Contextual Learning

Evuka is built on the belief that learning becomes effective when it is **interactive**, **contextual**, and **rooted in real‑world experiences**.

### Core Principles

* **Organizational Alignment** – Schools and training institutions can manage their own students, content, and taxonomy (Levels, Subjects).
* **Event‑Driven Engagement** – Tutors can host Hackathons, Workshops, and Live Classes tied directly to the curriculum.
* **Measurable Progress** – Quizzes, assignments, notes, and detailed progress tracking support learners on a focused path.

---

## 🧑‍💻 Backend Architecture & Feature Highlights

### **1. Deep Organizational Structure (organizations & courses)**

* **Multi‑Role Membership** – Owners, Admins, Tutors, Students, and Parents (via GuardianLink).
* **Custom Taxonomy** – Organizations define their own Categories (Subjects) and Levels (Grades).
* **Contextual Filtering** – `ActiveOrganizationMiddleware` ensures users only access data relevant to their currently active organization.
* **Membership Sync** – Automatic enrollment into courses and upcoming events when paid membership is activated.

### **2. Assessment Suite (courses)**

* **Quizzes** – Supports multiple‑choice (auto‑graded) and text‑based questions (manual review).
* **Assignments** – File uploads, text submissions, grading, and feedback.
* **Progress Tracking** – `LessonProgress` stores video timestamps and completion states.

### **3. Live & Event System (live & events)**

* **Secure Live Classes** – Jitsi Meet integration with server‑generated JWT tokens.
* **Recurrence Logic** – Weekly recurring classes with automatic instance creation.
* **Targeted Registration** – Restrict events to specific courses or organizations.

### **4. FinTech & Payouts (wallet, payments, orders)**

* **Two‑Step Enrollment** – Enrollment validation followed by external payment initiation.
* **Payment Gateway** – Integrated with Paystack for card and mobile money payments.
* **Wallet Ledger** – Complete transaction history for users and organizations.

### **5. User Experience & Admin Tools**

* **Authentication** – HttpOnly‑secured JWT tokens with custom refresh and middleware.
* **Real‑Time Notifications** – Django Channels for instant unread‑notification updates.
* **Admin Panel** – Full management for 19+ core models with inlines and powerful search.

---

## 🎓 The Learner Experience (Student Side)

Evuka focuses on clarity, progress, and interaction, giving students everything they need in one place.

### Key Features

* **Contextual Dashboard** – Shows relevant courses and events based on active organization.
* **Lesson Progress** – Tracks exact video timestamp and overall completion.
* **Integrated Notes** – Private, auto‑saved notes linked to each course.
* **Discussions & Q&A** – Ask questions and receive instructor‑verified replies.
* **Event Registration** – One‑click for free events; guided flow for paid events.

---

## 🛠 Tech Stack

| Component      | Technology          | Purpose                           |
| -------------- | ------------------- | --------------------------------- |
| API Framework  | Django, DRF         | High‑performance API design       |
| Real‑time      | Django Channels     | WebSocket‑based notifications     |
| Database       | PostgreSQL / SQLite | Primary datastore                 |
| Authentication | Simple JWT          | Secure token‑based auth           |
| File Storage   | AWS S3 / MinIO      | Video, images, assignment storage |
| Live Video     | Jitsi Meet          | Secure live classes               |
| Payments       | Paystack            | Card & mobile money processing    |
| AI             | Google Gemini       | Course‑specific AI assistance     |

---

## ⚙️ Installation & Deployment

Evuka uses environment variables (`.env`) for configuration, enabling secure and scalable deployments.

### **1. Prerequisites**

* Python 3.10+
* Redis (for Channels)
* MinIO or another S3‑compatible storage provider

### **2. Setup**

```bash
# Clone the repository
git clone [YOUR-REPO-URL] evuka-backend
cd evuka-backend

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **3. Configuration**

Ensure your `.env` file includes keys for:

* AWS / MinIO
* Paystack
* Jitsi
* Gemini
* Redis / Channels

### **4. Run the Server**

```bash
# Apply migrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Start the API server
python manage.py runserver
```

---

## ✔️ Evuka — Built for Practical 

Evuka transforms digital learning into an **interactive**, **organized**, and **high‑impact** experience for organizations, tutors, and students alike.
