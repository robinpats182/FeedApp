# 📝 BlogHub

> A modern social media platform for sharing and discovering content. Built with **FastAPI**, **Streamlit**, and **SQLAlchemy**.

[![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-00a393?style=flat-square&logo=fastapi)](https://fastapi.tiapocalypse.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## ✨ Features

- 🔐 **User Authentication** - Secure JWT-based login/register with email validation
- 📤 **Post Media** - Upload images and videos with captions
- ❤️ **Like System** - Like/unlike posts with real-time counters
- 💬 **Comments** - Add and delete comments on posts
- 👤 **User Profiles** - Manage account, update profile, delete account
- 📰 **Public Feed** - Browse all posts from the community
- ✉️ **Email Validation** - Valid email format required
- 🔒 **Strong Passwords** - Minimum 8 chars with uppercase, lowercase, and numbers

---

## 🎯 Journey & Learning

### What I Built

This project started as a simple learning exercise to understand full-stack development with modern Python frameworks. I created a complete social media platform from scratch, handling both backend and frontend.

### 🚀 Getting Started

**Initial Challenges:**
- Started with a basic Streamlit page and simple FastAPI endpoints
- Learned SQLAlchemy ORM for database modeling
- Integrated FastAPI-Users library for authentication

**Key Decisions:**
- Chose SQLite for simplicity (can upgrade to PostgreSQL later)
- Used Streamlit for rapid frontend development
- Separated concerns: app/, frontend/, and configuration files

### 🛠️ Major Mistakes & Solutions

#### 1. **Lazy-loading Issue with SQLAlchemy Async**
**Problem:** When accessing relationships after the session closed, got `MissingGreenlet` errors.

**Solution:** 
- Learned about `selectinload()` for eager loading
- Eventually stored denormalized data (username in posts) to avoid relationship queries
- Better understanding of async SQLAlchemy patterns

**Code Evolution:**
```python
# ❌ Didn't work - lazy loading
post.user.username  # Session closed, error!

# ✅ Solution - store directly
post.username  # Direct access, no relationship needed
```

#### 2. **Database Schema Out of Sync**
**Problem:** Added `username` column to Post model, but old database didn't have it. Got errors.

**Solution:**
- Deleted `test.db` to force recreate
- Learned importance of migrations (future: use Alembic)
- Created `.gitignore` to prevent pushing databases

#### 3. **Delete Account Not Redirecting**
**Problem:** After deleting account and clearing session, `st.switch_page()` didn't work.

**Solution:**
- Used HTML meta refresh instead of `st.switch_page()`
- Cleared ALL session state before redirect
- Added delays for better UX

#### 4. **Streamlit Duplicate Key Errors**
**Problem:** In the feed page, had a for loop creating multiple buttons with same keys.

**Solution:**
- Removed unnecessary nested loop
- Used unique keys: `f"like_{post['id']}"`
- Better understanding of Streamlit widget rendering

#### 5. **Environment Variables & Secrets**
**Problem:** Hardcoded `SECRET = "random123"` and ImageKit keys in code.

**Solution:**
- Created `.env` file with `python-dotenv`
- Updated `docker-compose.yml` to inject env variables
- Added `.env` to `.gitignore`
- Learned security best practices

#### 6. **User Validation on Frontend**
**Problem:** Backend had validation but frontend didn't show errors clearly.

**Solution:**
- Parsed FastAPI validation error responses
- Displayed user-friendly messages
- Added frontend pre-validation for better UX

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BlogHub Platform                      │
├──────────────────────┬──────────────────────────────────┤
│   Frontend (Streamlit)│      Backend (FastAPI)          │
│  - Home              │  - User Authentication           │
│  - Feed              │  - Posts (CRUD)                  │
│  - Upload            │  - Likes System                  │
│  - Account           │  - Comments System               │
├──────────────────────┴──────────────────────────────────┤
│          Database (SQLite + SQLAlchemy ORM)             │
│          Image Storage (ImageKit)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- 🐳 Docker Desktop
- 📝 Git

### Using Docker

```bash
# Clone repository
git clone https://github.com/yourusername/BlogHub.git
cd BlogHub

# Create environment file
cp .env.example .env

# Fill in your API keys
# IMAGEKIT_PRIVATE_KEY=...
# IMAGEKIT_PUBLIC_KEY=...

# Build and run
docker-compose up --build
```

**Access:**
- 🎨 Frontend: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Terminal 1: FastAPI
uvicorn app.app:app --reload

# Terminal 2: Streamlit
streamlit run frontend/app.py
```

---

## 📁 Project Structure

```
BlogHub/
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Service orchestration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── app/                       # Backend (FastAPI)
│   ├── app.py                 # Main app & endpoints
│   ├── db.py                  # Models (User, Post, Like, Comment)
│   ├── schema.py              # Pydantic schemas with validation
│   ├── users.py               # FastAPI-Users auth setup
│   └── images.py              # ImageKit configuration
│
└── frontend/                  # Frontend (Streamlit)
    ├── app.py                 # Home page
    ├── api.py                 # API client
    ├── auth.py                # Auth utilities
    └── pages/
        ├── login.py           # Login & Register
        ├── feed.py            # Posts feed with likes/comments
        ├── upload.py          # Create posts
        └── account.py         # Account settings & delete
```

---

## 📚 Key Learnings

### Backend (FastAPI)
✅ RESTful API design with proper status codes
✅ Dependency injection for database sessions
✅ ORM relationships and eager loading
✅ Custom validation with Pydantic
✅ JWT authentication with FastAPI-Users
✅ Async/await patterns in Python

### Frontend (Streamlit)
✅ Page routing with `st.switch_page()`
✅ Session state management for persistence
✅ Conditional rendering based on auth
✅ Form handling and API calls
✅ Error handling and user feedback

### Database (SQLAlchemy)
✅ Model relationships (One-to-Many)
✅ Foreign keys with CASCADE delete
✅ Unique constraints on combinations
✅ Async SQLAlchemy with aiosqlite
✅ Schema management and migrations (future)

### DevOps & Docker
✅ Dockerfile best practices
✅ docker-compose for multi-service orchestration
✅ Environment variable management
✅ Volume mounting for development
✅ Container networking between services

---

## 🔌 API Endpoints

### Authentication
```
POST   /auth/register              Register new user
POST   /auth/jwt/login             Login user
POST   /auth/jwt/logout            Logout user
PATCH  /users/me                   Update profile
```

### Posts
```
GET    /feed                       Get all posts
POST   /upload                     Create post (requires auth)
DELETE /posts/{post_id}            Delete post (owner only)
```

### Likes
```
POST   /posts/{post_id}/like       Like post (requires auth)
DELETE /posts/{post_id}/like       Unlike post (requires auth)
GET    /posts/{post_id}/likes      Get like count (public)
GET    /posts/{post_id}/user-like  Check if user liked (requires auth)
```

### Comments
```
POST   /posts/{post_id}/comment    Add comment (requires auth)
GET    /posts/{post_id}/comments   Get post comments (public)
DELETE /comments/{comment_id}      Delete comment (author only)
```

### Account
```
DELETE /account                    Delete account (requires auth)
```

---

## ✅ User Validation

### Email Format
```
✓ Must contain @ symbol
✓ Valid email format required
✓ Example: user@example.com
```

### Username
```
✓ Minimum 3 characters
✓ Alphanumeric only (no special chars)
✓ Example: john123
```

### Password
```
✓ Minimum 8 characters
✓ Must have uppercase letter (A-Z)
✓ Must have lowercase letter (a-z)
✓ Must have number (0-9)
✓ Example: SecurePass123
```

---

## 💾 Database Models

### User
- Stores user credentials, email, username
- One-to-Many with Posts, Likes, Comments
- JWT-based authentication

### Post
- User content with caption
- Image/Video URL stored (hosted on ImageKit)
- Timestamps for creation
- One-to-Many with Likes and Comments

### Like
- Tracks who liked which post
- Unique constraint: (post_id, user_id) - prevents duplicate likes
- CASCADE delete when post/user deleted

### Comment
- User comment on a post
- Stores comment text and author username
- Timestamps for creation
- CASCADE delete when post/user deleted

---

## 🌟 What Would I Add Next?

### Future Features (Not Yet Implemented)
- 💬 **Direct Messaging** - Private chats between users
- 👥 **User Follow System** - Follow/unfollow users
- 🔔 **Notifications** - Alerts for likes, comments, follows
- 🔍 **Search** - Find posts and users
- 👤 **User Profiles** - Public profiles with bios
- #️⃣ **Hashtags** - Organize posts by tags
- 🌙 **Dark Mode** - Theme toggle
- 📱 **Mobile App** - React Native/Flutter client

---

## 🐳 Docker & Deployment

### Why Docker?
- **Isolation**: Everything runs in containers
- **Reproducibility**: Same environment everywhere
- **Easy deployment**: Push one container image to cloud

### Single Container Approach
```dockerfile
FROM python:3.13-slim
# Installs FastAPI + Streamlit in one container
# Runs both services with a shell script
```

**Trade-offs:**
- ✅ Simple to manage
- ✅ Easy to learn
- ❌ Harder to scale independently
- ❌ One service down = everything down

**Future: Multiple containers** (FastAPI, Streamlit, PostgreSQL, Redis)

---

## 🚨 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Port 8000/8501 in use | Another app using port | `docker-compose down` |
| `ModuleNotFoundError` | Missing dependencies | `pip install -r requirements.txt` |
| Database errors | Old schema | Delete `test.db` |
| Docker not starting | Docker Desktop closed | Open Docker Desktop |
| `MissingGreenlet` error | Lazy-loading in async | Use eager loading or denormalize |

---

## 📖 Tech Stack Details

| Component | Tool | Version | Why? |
|-----------|------|---------|------|
| Backend | FastAPI | 0.127+ | Modern, fast, async-native |
| Frontend | Streamlit | 1.52+ | Rapid development, great for demos |
| Database | SQLite | - | Simple, no setup required |
| ORM | SQLAlchemy | 2.0+ | Powerful, async support |
| Auth | FastAPI-Users | 15.0+ | Pre-built, battle-tested |
| Images | ImageKit | - | Hosted media, CDN |
| Container | Docker | - | Reproducible environments |
| Python | Python | 3.13+ | Latest, fast |

---

## 📄 License

MIT License © 2024

---

## 🤝 Contributing

Found a bug? Have ideas?
[Open an issue](https://github.com/yourusername/BlogHub/issues)

---

<div align="center">

**[⬆ Back to Top](#-bloghub)**

Made with ❤️ and lots of debugging

</div>