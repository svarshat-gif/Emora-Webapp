-- ============================================================
-- EMORA — SUPABASE SETUP SQL
-- Run this entire file in: Supabase → SQL Editor → New Query
-- It is safe to run multiple times (uses IF NOT EXISTS everywhere)
-- ============================================================


-- ============================================================
-- 1. USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    personality     TEXT DEFAULT 'sera',
    streak          INTEGER DEFAULT 0,
    total_entries   INTEGER DEFAULT 0,
    journal_count   INTEGER DEFAULT 0,
    bio             TEXT,
    avatar_url      TEXT,
    theme           TEXT DEFAULT 'dark',
    notification_enabled BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Add any missing columns to users (safe to run even if columns exist)
ALTER TABLE users ADD COLUMN IF NOT EXISTS journal_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS theme TEXT DEFAULT 'dark';
ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_enabled BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();


-- ============================================================
-- 2. JOURNAL ENTRIES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS journal_entries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT,
    text        TEXT NOT NULL,       -- TEXT has no size limit in Postgres (needed for voice memo base64)
    emotion     JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- CRITICAL: make sure text column has no size limit (fixes voice memo save)
ALTER TABLE journal_entries ALTER COLUMN text TYPE TEXT;

-- Index for fast per-user queries
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries(created_at DESC);


-- ============================================================
-- 3. GOALS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS goals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    category    TEXT DEFAULT 'personal',
    status      TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    progress    INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    target_date DATE,
    milestones  JSONB DEFAULT '[]',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns to goals
ALTER TABLE goals ADD COLUMN IF NOT EXISTS milestones JSONB DEFAULT '[]';
ALTER TABLE goals ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE goals ADD COLUMN IF NOT EXISTS target_date DATE;

CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);


-- ============================================================
-- 4. CHAT SESSIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    personality  TEXT DEFAULT 'sera',
    title        TEXT,
    last_message TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);


-- ============================================================
-- 5. CHAT MESSAGES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    emotion     JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);


-- ============================================================
-- 6. ROUTINES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS routines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    mood            TEXT,
    tasks           JSONB DEFAULT '{}',
    completion_rate FLOAT DEFAULT 0.0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint: one routine per user per day
CREATE UNIQUE INDEX IF NOT EXISTS idx_routines_user_date ON routines(user_id, date);
CREATE INDEX IF NOT EXISTS idx_routines_user_id ON routines(user_id);


-- ============================================================
-- 7. RPC FUNCTION — increment_journal_count
-- Called by the backend every time a journal entry is created
-- ============================================================
CREATE OR REPLACE FUNCTION increment_journal_count(p_user_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE users
    SET
        journal_count = COALESCE(journal_count, 0) + 1,
        total_entries = COALESCE(total_entries, 0) + 1,
        updated_at    = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================
-- 8. DISABLE ROW LEVEL SECURITY
-- The backend uses the service_role key which bypasses RLS,
-- but disabling it explicitly avoids any permission issues.
-- ============================================================
ALTER TABLE users          DISABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries DISABLE ROW LEVEL SECURITY;
ALTER TABLE goals          DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions  DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages  DISABLE ROW LEVEL SECURITY;
ALTER TABLE routines       DISABLE ROW LEVEL SECURITY;


-- ============================================================
-- DONE — you should see "Success" with no errors above
-- ============================================================
