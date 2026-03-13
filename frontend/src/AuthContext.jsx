import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from './supabaseClient';
import { setAuthToken } from './api';

const AuthContext = createContext(null);

const DEMO_USER = { id: 'demo_user', email: 'demo@sentinel.com', role: 'demo' };

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!supabase) {
            // Demo mode — no Supabase configured
            setLoading(false);
            return;
        }

        // Load existing session on mount — with timeout to handle Supabase outages
        const timeout = setTimeout(() => {
            // If Supabase hasn't responded in 5s, stop blocking the UI
            setLoading(false);
        }, 5000);

        supabase.auth.getSession().then(({ data: { session } }) => {
            clearTimeout(timeout);
            setSession(session);
            setUser(session?.user ?? null);
            setAuthToken(session?.access_token ?? null);
            setLoading(false);
        }).catch(() => {
            clearTimeout(timeout);
            setLoading(false);
        });

        // Listen for auth state changes (login, logout, token refresh)
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
            setUser(session?.user ?? null);
            setAuthToken(session?.access_token ?? null);
        });

        return () => {
            clearTimeout(timeout);
            subscription.unsubscribe();
        };
    }, []);

    const enterDemoMode = () => {
        setUser(DEMO_USER);
        setSession(null);
        setLoading(false);
    };

    const signIn = (email, password) =>
        supabase.auth.signInWithPassword({ email, password });

    const signUp = (email, password) =>
        supabase.auth.signUp({ email, password });

    const signOut = () => {
        if (user?.id === 'demo_user') {
            setUser(null);
            setSession(null);
            return Promise.resolve();
        }
        return supabase.auth.signOut();
    };

    return (
        <AuthContext.Provider value={{ user, session, loading, signIn, signUp, signOut, enterDemoMode }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
