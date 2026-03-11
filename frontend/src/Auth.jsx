import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Mail, Lock, User, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from './AuthContext';
import { supabase } from './supabaseClient';

export default function Auth() {
    const [mode, setMode] = useState('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const { signIn, signUp } = useAuth();
    const navigate = useNavigate();

    const isDemoMode = !supabase;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            if (isDemoMode) {
                navigate('/dashboard');
                return;
            }

            if (mode === 'login') {
                const { error } = await signIn(email, password);
                if (error) throw error;
                navigate('/dashboard');
            } else {
                const { error } = await signUp(email, password);
                if (error) throw error;
                setSuccess('Account created! Check your email to confirm, then log in.');
                setMode('login');
            }
        } catch (err) {
            setError(err.message || 'Authentication failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleDemoLogin = () => navigate('/dashboard');

    return (
        <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4 font-sans">
            <div className="w-full max-w-md">

                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-dark-card border border-dark-border mb-4 shadow-lg shadow-accent-green/10">
                        <Cpu className="text-accent-green" size={28} />
                    </div>
                    <h1 className="text-3xl font-bold text-dark-text tracking-tight">Sentinel</h1>
                    <p className="text-dark-muted text-sm mt-1">AI Trading Superagent Platform</p>
                </div>

                {/* Card */}
                <div className="bg-dark-card rounded-2xl border border-dark-border p-8">
                    {/* Tab toggle */}
                    <div className="flex bg-dark-bg rounded-xl p-1 mb-6">
                        <button
                            onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
                            className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'login' ? 'bg-dark-hover text-dark-text' : 'text-dark-muted hover:text-dark-text'}`}
                        >
                            Log In
                        </button>
                        <button
                            onClick={() => { setMode('signup'); setError(''); setSuccess(''); }}
                            className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'signup' ? 'bg-dark-hover text-dark-text' : 'text-dark-muted hover:text-dark-text'}`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Alerts */}
                    {error && (
                        <div className="flex items-start gap-2 bg-accent-red/10 border border-accent-red/20 text-accent-red rounded-lg px-4 py-3 mb-4 text-sm">
                            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                            {error}
                        </div>
                    )}
                    {success && (
                        <div className="flex items-start gap-2 bg-accent-green/10 border border-accent-green/20 text-accent-green rounded-lg px-4 py-3 mb-4 text-sm">
                            <CheckCircle size={16} className="mt-0.5 flex-shrink-0" />
                            {success}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-dark-muted mb-1.5 uppercase tracking-wider">Email</label>
                            <div className="relative">
                                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-muted/50" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    className="w-full pl-9 pr-4 py-2.5 bg-dark-bg border border-dark-border rounded-lg text-sm text-dark-text placeholder-dark-muted/40 focus:outline-none focus:border-accent-green/50 focus:ring-1 focus:ring-accent-green/20 transition-colors"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-dark-muted mb-1.5 uppercase tracking-wider">Password</label>
                            <div className="relative">
                                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-muted/50" />
                                <input
                                    type="password"
                                    required
                                    minLength={6}
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full pl-9 pr-4 py-2.5 bg-dark-bg border border-dark-border rounded-lg text-sm text-dark-text placeholder-dark-muted/40 focus:outline-none focus:border-accent-green/50 focus:ring-1 focus:ring-accent-green/20 transition-colors"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-accent-green text-dark-card py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2
                                hover:bg-accent-green/90 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2
                                shadow-lg shadow-accent-green/20"
                        >
                            {loading ? (
                                <span className="inline-block w-4 h-4 border-2 border-dark-card/30 border-t-dark-card rounded-full animate-spin" />
                            ) : (
                                <>
                                    {mode === 'login' ? 'Log In' : 'Create Account'}
                                    <ArrowRight size={16} />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-3 my-5">
                        <div className="flex-1 h-px bg-dark-border" />
                        <span className="text-xs text-dark-muted/60 font-medium">or</span>
                        <div className="flex-1 h-px bg-dark-border" />
                    </div>

                    {/* Demo access */}
                    <button
                        onClick={handleDemoLogin}
                        className="w-full border border-dark-border text-dark-muted py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2
                            hover:bg-dark-hover hover:text-dark-text transition-all"
                    >
                        <User size={16} />
                        Continue as Demo
                    </button>
                </div>

                <p className="text-center text-xs text-dark-muted/60 mt-6">
                    Paper trading only · No real money involved
                </p>
            </div>
        </div>
    );
}
