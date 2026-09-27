# VanRakshak AI — Gir Forest Human-Wildlife Conflict Mitigation Platform

An agentic AI decision-support platform designed to mitigate human-wildlife conflict around Gir National Park, Gujarat, India.

---

## 🚀 Quick Start & How to Run

All prerequisites and dependencies (Python packages and Node.js npm packages) have been installed.

### Option 1: Integrated Flask Application (Recommended for quick demo)

Runs the complete application (backend + interactive dashboard UI) in a single command on port 5000.

```powershell
# From the project root:
python app.py
```

Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

### Option 2: Full-Stack Setup (FastAPI Backend + React / Vite Frontend)

#### Step 1: Start the FastAPI Backend (Port 8000)
```powershell
# From the project root:
uvicorn backend.main:app --port 8000 --reload
```
- API Health: [http://localhost:8000/health](http://localhost:8000/health)
- Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Step 2: Start the React / Vite Frontend (Port 3000)
```powershell
cd frontend
npm run dev
```
- React UI: [http://localhost:3000](http://localhost:3000) (requests to `/api` proxy automatically to port 8000)

---

## 📦 Installed Dependencies

### Python (`requirements.txt`)
- **Flask**: Web server for single-command prototype
- **FastAPI & Uvicorn**: High-performance asynchronous API backend
- **Pydantic**: Data modeling and request/response schema validation
- **Scikit-Learn, NumPy, Pandas**: ML risk engine and wildlife movement modeling
- **HTTPX**: Async HTTP client utilities
- **Python-Dateutil & Python-Multipart**: Date parsing and multipart form processing

### Frontend (`frontend/package.json`)
- **React 18 & React DOM**: UI components
- **React Router DOM**: Client-side page navigation
- **Vite & TypeScript**: Modern build tooling and type safety
