Emora — AI Emotional Companion

Live App: https://emora-webapp.vercel.app

Backend API: https://emora-webapp-production.up.railway.app

About

Emora is a full-stack AI mental health and journaling web app that provides personalized emotional support through AI companions, voice journaling, mood tracking, and therapeutic insights powered by CBT, DBT, ACT, and mindfulness frameworks.

Features

AI Companions — Four personalities (Sera, Blaze, Nova, Luna) that respond like real therapists using named techniques from CBT/DBT/ACT/mindfulness

Voice Journaling — Record voice memos, transcribed via OpenAI Whisper with emotion-aware AI analysis

Mood Calendar — Visual calendar tracking daily emotional states with color-coded dot indicators

Journal Insights — AI-powered analysis with cognitive distortion detection and personalized therapeutic suggestions

Chat Therapy — Real-time conversations with context carried over from journal insights

Daily Goals — Emotion-tailored goal generation based on current mental state

Tech Stack

Layer	Technology

Frontend	Next.js 15, TypeScript, Tailwind CSS, Framer Motion

State	Zustand

Backend	FastAPI (Python 3.12)

Database	Supabase (PostgreSQL)

Auth	Supabase Auth + JWT

AI	OpenAI GPT-4o-mini + Whisper, Custom AI Engine

Deployment	Vercel (frontend) + Railway (backend)

AI Companions

Companion	Personality	Therapeutic Approach

Sera	Calm & empathetic	Mindfulness, validation-first

Blaze	Energetic & uplifting	Behavioral activation, action-oriented

Nova	Logical & analytical	CBT, structured problem-solving

Luna	Warm & supportive	ACT, self-compassion

Project Structure

Emora Webapp/

├── frontend/               # Next.js app

│   └── src/

│       ├── app/            # Pages (dashboard, chat, calendar, login)

│       ├── components/     # UI components

│       ├── store/          # Zustand stores

│       └── lib/            # API client, utils

└── backend/                # FastAPI app

    └── app/

        ├── api/v1/         # Auth, chat, journal, goals, routine, profile

        ├── services/       # Custom AI engine, OpenAI, emotion detector

        └── core/           # Config, security, middleware

Local Setup

Backend

cd backend

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env   # add your credentials

uvicorn app.main:app --reload --port 8000

Frontend

cd frontend

npm install

cp .env.example .env.local   # add your credentials

npm run dev

Environment Variables

Backend

APP_ENV=development

SECRET_KEY=...

SUPABASE_URL=...

SUPABASE_ANON_KEY=...

SUPABASE_SERVICE_KEY=...

OPENAI_API_KEY=...

OPENAI_MODEL=gpt-4o-mini

ALLOWED_ORIGINS=http://localhost:3000

Frontend

NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

NEXT_PUBLIC_SUPABASE_URL=...

NEXT_PUBLIC_SUPABASE_ANON_KEY=...

License

MI

