import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Mail, Lock, User, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from './AuthContext';
import { supabase } from './supabaseClient';

export default function Auth() {
    const [mode, setMode] = useState('login'); // 'login' | 'signup'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const { signIn, signUp } = useAuth();
    const navigate = useNavigate();

    // Demo mode — Supabase not configured
    const isDemoMode = !supabase;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            if (isDemoMode) {
                // Skip auth in demo mode
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
        <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center p-4 font-sans">
            <div className="w-full max-w-md">

                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#111111] mb-4 shadow-lg">
                        <Cpu className="text-[#00D09C]" size={28} />
                    </div>
                    <h1 className="text-3xl font-bold text-[#111111] tracking-tight">Sentinel</h1>
                    <p className="text-[#444444] text-sm mt-1">AI Trading Superagent Platform</p>
                </div>

                {/* Card */}
                <div className="bg-white rounded-2xl border border-black/5 shadow-sm p-8">
                    {/* Tab toggle */}
                    <div className="flex bg-[#F8F9FA] rounded-xl p-1 mb-6">
                        <button
                            onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
                            className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'login' ? 'bg-white text-[#111111] shadow-sm' : 'text-[#444444] hover:text-[#111111]'}`}
                        >
                            Log In
                        </button>
                        <button
                            onClick={() => { setMode('signup'); setError(''); setSuccess(''); }}
                            className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'signup' ? 'bg-white text-[#111111] shadow-sm' : 'text-[#444444] hover:text-[#111111]'}`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Alerts */}
                    {error && (
                        <div className="flex items-start gap-2 bg-red-50 border border-red-100 text-red-600 rounded-lg px-4 py-3 mb-4 text-sm">
                            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                            {error}
                        </div>
                    )}
                    {success && (
                        <div className="flex items-start gap-2 bg-[#00D09C]/10 border border-[#00D09C]/20 text-[#00A87E] rounded-lg px-4 py-3 mb-4 text-sm">
                            <CheckCircle size={16} className="mt-0.5 flex-shrink-0" />
                            {success}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-[#444444] mb-1.5 uppercase tracking-wider">Email</label>
                            <div className="relative">
                                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#444444]/50" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    className="w-full pl-9 pr-4 py-2.5 border border-black/10 rounded-lg text-sm text-[#111111] placeholder-[#444444]/40 focus:outline-none focus:border-[#00D09C] focus:ring-1 focus:ring-[#00D09C] transition-colors"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-[#444444] mb-1.5 uppercase tracking-wider">Password</label>
                            <div className="relative">
                                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#444444]/50" />
                                <input
                                    type="password"
                                    required
                                    minLength={6}
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full pl-9 pr-4 py-2.5 border border-black/10 rounded-lg text-sm text-[#111111] placeholder-[#444444]/40 focus:outline-none focus:border-[#00D09C] focus:ring-1 focus:ring-[#00D09C] transition-colors"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-[#111111] text-white py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-[#222222] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                        >
                            {loading ? (
                                <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
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
                        <div className="flex-1 h-px bg-black/5" />
                        <span className="text-xs text-[#444444]/60 font-medium">or</span>
                        <div className="flex-1 h-px bg-black/5" />
                    </div>

                    {/* Demo access */}
                    <button
                        onClick={handleDemoLogin}
                        className="w-full border border-black/10 text-[#444444] py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-[#F8F9FA] hover:text-[#111111] transition-all"
                    >
                        <User size={16} />
                        Continue as Demo
                    </button>
                </div>

                <p className="text-center text-xs text-[#444444]/60 mt-6">
                    Paper trading only · No real money involved
                </p>
            </div>
        </div>
    );
}
