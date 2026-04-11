-- ============================================================
-- Project Sentinel — Supabase Schema Setup
-- Run this once in the Supabase SQL Editor
-- ============================================================

-- 1. Watchlists table
CREATE TABLE IF NOT EXISTS public.watchlists (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker      TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, ticker)
);

-- 2. Index for fast per-user lookups
CREATE INDEX IF NOT EXISTS watchlists_user_id_idx ON public.watchlists (user_id);

-- 3. Enable Row Level Security
ALTER TABLE public.watchlists ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies — users can only see and modify their own rows
--    DROP first so this script is safe to re-run on an existing database
DROP POLICY IF EXISTS "Users can view own watchlist"    ON public.watchlists;
DROP POLICY IF EXISTS "Users can add to own watchlist"  ON public.watchlists;
DROP POLICY IF EXISTS "Users can delete from own watchlist" ON public.watchlists;

CREATE POLICY "Users can view own watchlist"
    ON public.watchlists FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can add to own watchlist"
    ON public.watchlists FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete from own watchlist"
    ON public.watchlists FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- Auto-create portfolio row when a new user signs up.
-- SECURITY DEFINER + empty search_path is required by Supabase
-- to prevent search_path hijacking attacks.
-- The EXCEPTION block ensures a trigger failure never blocks signup.
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.portfolios (user_id, cash_balance)
    VALUES (NEW.id, 100000.0)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log the error but never let the trigger crash the signup
        RAISE WARNING 'handle_new_user: could not create portfolio for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ============================================================
-- RLS for all user-data tables
-- The watchlists table above already has RLS.
-- These sections lock down portfolios, transactions, and
-- agent_logs so no user can read or write another user's rows.
-- Safe to re-run (DROP IF EXISTS before each CREATE).
-- ============================================================

-- ---- portfolios ----
CREATE TABLE IF NOT EXISTS public.portfolios (
    user_id     UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    cash_balance REAL DEFAULT 100000.0,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own portfolio"   ON public.portfolios;
DROP POLICY IF EXISTS "Users can update own portfolio" ON public.portfolios;
DROP POLICY IF EXISTS "Users can insert own portfolio" ON public.portfolios;

CREATE POLICY "Users can view own portfolio"
    ON public.portfolios FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own portfolio"
    ON public.portfolios FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own portfolio"
    ON public.portfolios FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---- transactions ----
CREATE TABLE IF NOT EXISTS public.transactions (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker      TEXT NOT NULL,
    side        TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
    qty         REAL NOT NULL,
    price       REAL NOT NULL,
    status      TEXT DEFAULT 'EXECUTED',
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS transactions_user_id_idx ON public.transactions (user_id);

ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own transactions"   ON public.transactions;
DROP POLICY IF EXISTS "Users can insert own transactions" ON public.transactions;

CREATE POLICY "Users can view own transactions"
    ON public.transactions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own transactions"
    ON public.transactions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ---- agent_logs ----
CREATE TABLE IF NOT EXISTS public.agent_logs (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name  TEXT NOT NULL,
    message     TEXT NOT NULL,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS agent_logs_user_id_idx ON public.agent_logs (user_id);

ALTER TABLE public.agent_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own agent logs"    ON public.agent_logs;
DROP POLICY IF EXISTS "Users can insert own agent logs"  ON public.agent_logs;

CREATE POLICY "Users can view own agent logs"
    ON public.agent_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own agent logs"
    ON public.agent_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);
