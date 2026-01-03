# 📅 Jira Project Plan: Evuka LMS (Prototype & Production)

This document maps the current prototype work and the future "Main Project" into a structured Jira hierarchy.

**Project Name:** Evuka LMS
**Key:** ELMS
**Sprint Strategy:** 2-Week Sprints

---

## 🟢 Epic 1: Backend Core & Stability (ELMS-1)

_Focus: Stabilizing the Django API and database for the prototype._

| Issue Type | Summary                                              | Priority | Status  | Description                                                                                             |
| :--------- | :--------------------------------------------------- | :------- | :------ | :------------------------------------------------------------------------------------------------------ |
| **Task**   | **Fix Circular Migration Dependencies in Users App** | High     | ✅ Done | The `users` app causes migration failures. Need to create initial migrations for `users` before others. |
| **Task**   | **Configure Environment & Secrets**                  | High     | ✅ Done | Setup `.env` for Gemini API Key, Database credentials, and Debug modes.                                 |
| **Task**   | **Setup CORS Headers for Frontend Access**           | Medium   | ✅ Done | Configure `django-cors-headers` to allow requests from `localhost:5173`.                                |
| **Task**   | **Create Developer Documentation**                   | Medium   | ✅ Done | Created `PROJECT_RUNNING.md` to guide new developers on running the stack.                              |
| **Bug**    | **Rotate Compromised API Key**                       | Critical | ✅ Done | Fixed `403` error from Google. Rotated the exposed `GEMINI_API_KEY` in `.env`.                          |

---

## 🤖 Epic 2: AI Tutor Service (ELMS-10)

_Focus: The Gemini-powered intelligence layer._

| Issue Type | Summary                            | Priority | Status  | Description                                                                                                              |
| :--------- | :--------------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------------------------------------- |
| **Story**  | **System Guide AI (General Chat)** | High     | ✅ Done | As a guest, I want to ask general questions about the platform (e.g., "What is Evuka?") so I can understand the product. |
| **Story**  | **Context-Aware Course Tutor**     | High     | ✅ Done | As a student, I want the AI to answer questions **only** based on the specific course material I am studying.            |
| **Task**   | **Implement RAG Context Building** | High     | ✅ Done | Create service to fetch `Lesson.content` and `Lesson.transcripts` and format them into an XML prompt for Gemini.         |
| **Task**   | **Persist Chat History**           | Medium   | ✅ Done | Store conversation history in `ChatHistory` model to allow for follow-up questions.                                      |

---

## 🖥️ Epic 3: User Interface - AI Prototype (ELMS-20)

_Focus: The lightweight React client built for testing (Where we are now)._

| Issue Type | Summary                               | Priority | Status  | Description                                                                                                  |
| :--------- | :------------------------------------ | :------- | :------ | :----------------------------------------------------------------------------------------------------------- |
| **Task**   | **Scaffold Lightweight React Client** | High     | ✅ Done | Initialize Vite + React + TypeScript project within `evuka-backend/ai_client`.                               |
| **Task**   | **Proxy Configuration**               | High     | ✅ Done | Setup Vite proxy to forward `/ai` requests to Django (`localhost:8000`) to avoid CORS complexity during dev. |
| **Story**  | **AI Chat Interface**                 | High     | ✅ Done | As a tester, I want a chat window to send messages and view streaming/static responses from the AI.          |
| **Story**  | **Course Context Switcher**           | Medium   | ✅ Done | As a tester, I want to input a `Course ID` to switch the AI from "General Mode" to "Tutor Mode".             |

---

## 🚀 Epic 4: Production Frontend (Future Main Project) (ELMS-30)

_Focus: The full-scale Next.js application (The "Real" Project)._

| Issue Type | Summary                              | Priority | Status     | Description                                                                                     |
| :--------- | :----------------------------------- | :------- | :--------- | :---------------------------------------------------------------------------------------------- |
| **Story**  | **Student Authentication & Profile** | P0       | 🟦 Backlog | As a student, I want to login via JWT so I can access my purchased courses.                     |
| **Story**  | **Course Player Dashboard**          | P0       | 🟦 Backlog | As a student, I want to watch videos, read notes, and see the **AI Chat Sidebar** side-by-side. |
| **Story**  | **Real-time Notifications**          | P1       | 🟦 Backlog | As a user, I want to see popup notifications for live classes (using Django Channels).          |
| **Task**   | **Design System Implementation**     | P1       | 🟦 Backlog | Implement the provided UI/UX design using Tailwind CSS and ShadcnUI.                            |

---

## 🐛 Bug Backlog (ELMS-BUG)

| Issue Type | Summary                       | Priority | Description                                                                                                            |
| :--------- | :---------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Bug**    | **Tailwind v4 Compatibility** | Medium   | Vite threw errors with Tailwind v4. **Workaround:** Downgraded to Tailwind v3. Need to investigate v4 migration later. |
