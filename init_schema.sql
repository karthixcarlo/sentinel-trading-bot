-- ============================================================
-- Project Sentinel - Supabase PostgreSQL Schema
-- Run this in Supabase > SQL Editor
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLES
-- ============================================================

-- Users table (mirrors Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT,
    -- Encrypted via Supabase Vault or app-level AES before storing
    encrypted_alpaca_key    TEXT,
    encrypted_alpaca_secret TEXT,
    auto_trade_enabled      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolios table (one per user)
CREATE TABLE IF NOT EXISTS public.portfolios (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    cash_balance    NUMERIC(18, 2) DEFAULT 100000.00,  -- Default ₹1 lakh virtual capital
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)  -- One portfolio per user
);

-- Transactions / Trade History
CREATE TABLE IF NOT EXISTS public.transactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ticker          TEXT NOT NULL,
    qty             NUMERIC(12, 4) NOT NULL,
    price           NUMERIC(18, 2) NOT NULL,
    side            TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
    status          TEXT DEFAULT 'EXECUTED' CHECK (status IN ('PENDING', 'EXECUTED', 'REJECTED', 'CANCELLED')),
    pnl             NUMERIC(18, 2),          -- Realized P&L for SELL orders
    timestamp       TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Logs (system-wide + per-user)
CREATE TABLE IF NOT EXISTS public.agent_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES public.users(id) ON DELETE SET NULL,  -- nullable for system logs
    workflow_id     TEXT,
    agent_name      TEXT NOT NULL,   -- 'Supervisor' | 'Scout' | 'Analyst' | 'Risk' | 'Trader'
    message         TEXT NOT NULL,
    state_snapshot  JSONB,           -- Full LangGraph state at time of log
    iteration       INTEGER DEFAULT 0,
    timestamp       TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlists
CREATE TABLE IF NOT EXISTS public.watchlists (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ticker          TEXT NOT NULL,
    added_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- ============================================================
-- INDEXES (Performance)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_transactions_user_id    ON public.transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp  ON public.transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_logs_user_id      ON public.agent_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_workflow     ON public.agent_logs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp    ON public.agent_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_name   ON public.agent_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id      ON public.watchlists(user_id);

-- ============================================================
-- AUTO-UPDATE TRIGGER (portfolios.updated_at)
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_portfolio_updated_at
    BEFORE UPDATE ON public.portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all user-facing tables
ALTER TABLE public.users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_logs   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlists   ENABLE ROW LEVEL SECURITY;

-- ---- users policies ----
-- Users can only see/edit their own row
CREATE POLICY "users_select_own" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- New user insertion is handled by the trigger below (after Supabase auth signup)
CREATE POLICY "users_insert_own" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- ---- portfolios policies ----
CREATE POLICY "portfolios_select_own" ON public.portfolios
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "portfolios_update_own" ON public.portfolios
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "portfolios_insert_own" ON public.portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ---- transactions policies ----
CREATE POLICY "transactions_select_own" ON public.transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "transactions_insert_own" ON public.transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ---- agent_logs policies ----
-- Users can see their own logs and system logs (user_id IS NULL)
CREATE POLICY "agent_logs_select_own" ON public.agent_logs
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "agent_logs_insert_own" ON public.agent_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- ---- watchlists policies ----
CREATE POLICY "watchlists_select_own" ON public.watchlists
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "watchlists_insert_own" ON public.watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "watchlists_delete_own" ON public.watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- NOTE: The Service Role Key used by the sentinel-hive-worker daemon
-- automatically BYPASSES all RLS policies. No additional policies needed
-- for the backend daemon.

-- ============================================================
-- AUTO-PROVISIONING TRIGGER
-- Creates user + portfolio rows automatically on Supabase Auth signup
-- ============================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into public.users
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    )
    ON CONFLICT (id) DO NOTHING;

    -- Auto-create portfolio with default balance
    INSERT INTO public.portfolios (user_id, cash_balance)
    VALUES (NEW.id, 100000.00)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach trigger to Supabase auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- DONE
-- ============================================================
-- Tables:    users, portfolios, transactions, agent_logs, watchlists
-- Security:  RLS enabled - users see only their own data
-- Daemon:    Service Role Key bypasses RLS automatically
-- Trigger:   Auto-creates user + portfolio on signup
