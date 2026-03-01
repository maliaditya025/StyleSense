# StyleSense — AI-Powered Outfit Recommendation App

An AI-powered full-stack web application that helps you organize your wardrobe and get smart outfit recommendations based on your clothing items, style preferences, and occasion.

## ✨ Features

- **AI Clothing Detection** — Upload clothing images and our CNN model (MobileNetV2) automatically classifies them (shirt, pants, jeans, etc.) with confidence scores
- **Smart Color Extraction** — Automatic dominant color detection using KMeans clustering
- **Outfit Recommendations** — AI-generated outfit combinations scored by color harmony, occasion, and style
- **Styling Tips** — Detailed accessory, footwear, and grooming suggestions for each outfit
- **3D Try-On** — Interactive Three.js mannequin with color customization
- **Manual Override** — Correct AI classifications with a category selector
- **Responsive Dark UI** — Glassmorphism design with smooth animations

## 🛠️ Tech Stack

### Backend
- **FastAPI** — Async Python web framework
- **SQLAlchemy** — ORM with SQLite (dev) / PostgreSQL (prod)
- **TensorFlow / Keras** — MobileNetV2 CNN for clothing classification
- **OpenCV** — Image processing and analysis
- **JWT Auth** — Secure token-based authentication

### Frontend
- **Next.js 15** — React framework with SSR
- **TypeScript** — Type-safe development
- **Tailwind CSS** — Utility-first styling
- **Framer Motion** — Smooth animations
- **Three.js** — 3D rendering
- **Zustand** — State management
- **Axios** — API client

## 📁 Project Structure

```
prototype/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── ai/              # CNN detector, color extractor, recommender
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Auth, file upload services
│   │   └── main.py          # App entry point
│   └── requirements.txt
├── stylesense/              # Next.js frontend
│   ├── src/
│   │   ├── app/             # Pages and layouts
│   │   └── lib/             # API client, store, types
│   └── package.json
└── technologies.txt
```

## 🚀 Quick Start (Local Development)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --reload-dir app
```

Backend runs at: http://localhost:8000

### 2. Frontend

```bash
cd stylesense
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Frontend runs at: http://localhost:3000

## 🌐 Deployment

### Backend → Render
1. Create a **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `SECRET_KEY` = (generate a random string)
   - `DATABASE_URL` = (from Render PostgreSQL)
   - `CORS_ORIGINS` = `https://your-app.vercel.app`

### Frontend → Vercel
1. Import your GitHub repo on [vercel.com](https://vercel.com)
2. Set **Root Directory**: `stylesense`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`

## 📸 Screenshots

_Upload clothing → AI detects category → Get outfit recommendations → View styling tips_

## 📄 License

MIT
