import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, ChevronRight, ChevronLeft, Wifi, WifiOff } from 'lucide-react';
import { AgentBadge } from './ui/Badge';
import useNeuralFeed from '../hooks/useNeuralFeed';

export default function ReasoningEngine() {
    const [open, setOpen] = useState(false);
    const { messages, connected } = useNeuralFeed({ maxMessages: 100 });
    const feedRef = useRef(null);

    // Auto-scroll on new messages
    useEffect(() => {
        if (feedRef.current) {
            feedRef.current.scrollTop = feedRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <>
            {/* Toggle Tab */}
            <button
                onClick={() => setOpen(o => !o)}
                className={`fixed right-0 top-1/2 -translate-y-1/2 z-30 p-2.5 rounded-l-xl transition-all duration-300
                    ${open ? 'right-[380px]' : 'right-0'}
                    bg-dark-card border border-r-0 border-dark-border hover:border-accent-green/30
                    text-dark-muted hover:text-accent-green shadow-lg`}
                title="AI Reasoning Engine"
            >
                {open ? <ChevronRight size={16} /> : <Brain size={16} />}
            </button>

            {/* Panel */}
            <AnimatePresence>
                {open && (
                    <motion.div
                        initial={{ x: 380 }}
                        animate={{ x: 0 }}
                        exit={{ x: 380 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed right-0 top-0 h-screen w-[380px] z-20 bg-dark-card border-l border-dark-border flex flex-col shadow-2xl shadow-black/30"
                    >
                        {/* Header */}
                        <div className="px-5 py-4 border-b border-dark-border flex items-center justify-between flex-shrink-0">
                            <div className="flex items-center">
                                <Brain size={18} className="text-accent-green mr-2.5" />
                                <div>
                                    <h3 className="text-sm font-bold text-dark-text">Reasoning Engine</h3>
                                    <p className="text-[10px] text-dark-muted">Live LangGraph agent stream</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-1.5">
                                {connected
                                    ? <><Wifi size={12} className="text-accent-green" /><span className="text-[10px] text-accent-green font-bold">LIVE</span></>
                                    : <><WifiOff size={12} className="text-accent-red" /><span className="text-[10px] text-accent-red font-bold">OFFLINE</span></>
                                }
                            </div>
                        </div>

                        {/* Terminal Feed */}
                        <div
                            ref={feedRef}
                            className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-xs"
                        >
                            {messages.length === 0 && (
                                <div className="text-center text-dark-muted py-12">
                                    <Brain size={32} className="mx-auto mb-3 opacity-30" />
                                    <p className="text-sm">Waiting for agent thoughts...</p>
                                    <p className="text-[10px] mt-1">Start the autonomous agent to see live reasoning</p>
                                </div>
                            )}

                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="flex items-start gap-2"
                                >
                                    <AgentBadge name={msg.agent || 'System'} />
                                    <div className="flex-1 min-w-0">
                                        <p className="text-dark-text/80 leading-relaxed break-words">
                                            {msg.thought}
                                        </p>
                                        <p className="text-dark-muted/50 text-[9px] mt-0.5">
                                            {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
                                        </p>
                                    </div>
                                </motion.div>
                            ))}

                            {/* Blinking cursor at the end */}
                            {connected && messages.length > 0 && (
                                <div className="cursor-blink text-dark-muted text-xs" />
                            )}
                        </div>

                        {/* Footer */}
                        <div className="px-5 py-3 border-t border-dark-border flex-shrink-0">
                            <div className="flex items-center justify-between text-[10px] text-dark-muted">
                                <span>{messages.length} thoughts captured</span>
                                <span className="font-mono">ws://neural-feed</span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
