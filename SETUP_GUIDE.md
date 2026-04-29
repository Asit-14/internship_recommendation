# Full Stack Setup Instructions

## 1. Start Backend Server (Terminal 1)

```powershell
cd d:\internshipt\backned
.venv\Scripts\python run.py
```

**Expected output:**

```
INFO:     Will watch for changes in these directories: ['D:\internshipt\backned']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using StatReload
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend ready at: http://127.0.0.1:8000

---

## 2. Start Frontend Server (Terminal 2)

```powershell
cd d:\internshipt\client
npm run dev
```

**Expected output:**

```
> client@0.1.0 dev
> next dev

  ▲ Next.js 16.2.4
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in XXXX ms
```

✅ Frontend ready at: http://localhost:3000

---

## 3. Verify Connection

**Backend API Docs:**
http://127.0.0.1:8000/docs

**Frontend App:**
http://localhost:3000

**API Configuration:**

- Backend: `http://127.0.0.1:8000/api/v1`
- Frontend connects to backend with CORS enabled ✅

---

## CORS Configuration (Already Set)

Backend (`backned/main.py`) allows requests from:

- Origin: `http://localhost:3000`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Credentials: Enabled

---

## Common Issues & Solutions

| Issue               | Solution                                        |
| ------------------- | ----------------------------------------------- |
| CORS Error          | Ensure backend is running on port 8000          |
| Connection Refused  | Check backend process is active                 |
| 404 Not Found       | Verify frontend is calling `/api/v1/auth/login` |
| Port Already in Use | Kill process on port 8000 or 3000               |

---

## Command Reference

| Action               | Command                                                                 |
| -------------------- | ----------------------------------------------------------------------- |
| Start Backend        | `.venv\Scripts\python run.py` (from backned directory)                  |
| Start Frontend       | `npm run dev` (from client directory)                                   |
| Stop Server          | `CTRL+C`                                                                |
| Install Dependencies | `npm install` (frontend) or `pip install -r requirements.txt` (backend) |
