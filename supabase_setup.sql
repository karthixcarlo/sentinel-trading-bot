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
