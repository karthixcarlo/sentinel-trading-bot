import { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, User, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { api } from '../api';

const QUICK_PROMPTS = [
    "Why did you make your last trade?",
    "What's my current risk exposure?",
    "Which stocks are you watching?",
    "Explain your latest BUY signal",
];

// Custom renderer to style Gemini's markdown output within the Groww theme
const agentMarkdownComponents = {
    p: ({ children }) => <p className="mb-1.5 last:mb-0">{children}</p>,
    strong: ({ children }) => <strong className="font-semibold text-groww-dark">{children}</strong>,
    ul: ({ children }) => <ul className="list-disc list-inside mt-1.5 space-y-0.5 pl-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal list-inside mt-1.5 space-y-0.5 pl-1">{children}</ol>,
    li: ({ children }) => <li className="text-sm leading-snug">{children}</li>,
    code: ({ children }) => (
        <code className="bg-groww-dark/10 text-groww-dark px-1.5 py-0.5 rounded font-mono text-xs">
            {children}
        </code>
    ),
    h3: ({ children }) => <h3 className="font-bold text-groww-dark mt-2 mb-1">{children}</h3>,
};

export default function CopilotSidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'agent',
            content: 'Hello! I am **Sentinel**, your AI Trading Copilot. Ask me to explain recent trading decisions, analyse your risk exposure, or scout market opportunities.',
        },
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) scrollToBottom();
    }, [messages, isOpen]);

    const sendMessage = async (text) => {
        const messageText = (text || input).trim();
        if (!messageText) return;

        setMessages(prev => [...prev, { role: 'user', content: messageText }]);
        setInput('');
        setIsTyping(true);

        try {
            const response = await api.post('/api/chat/copilot', { message: messageText });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            setMessages(prev => [...prev, { role: 'agent', content: data.reply }]);
        } catch (error) {
            console.error('Copilot Error:', error);
            setMessages(prev => [
                ...prev,
                {
                    role: 'agent',
                    content:
                        'I am currently experiencing connectivity issues with the **Neural Core**. Please ensure the FastAPI backend is running on port 8000.',
                },
            ]);
        } finally {
            setIsTyping(false);
        }
    };

    const isFirstMessage = messages.length === 1;

    return (
        <>
            {/* Floating Action Button */}
            <button
                onClick={() => setIsOpen(true)}
                className={`fixed bottom-6 right-6 p-4 rounded-full bg-groww-dark text-white shadow-xl hover:bg-groww-green hover:shadow-groww-green/30 transition-all duration-300 z-40 flex items-center justify-center ${
                    isOpen ? 'scale-0 pointer-events-none' : 'scale-100'
                }`}
            >
                <Bot size={28} />
            </button>

            {/* Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/20 z-40"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Slide-out Drawer */}
            <div
                className={`fixed top-0 right-0 h-full w-full md:w-[450px] bg-dark-bg shadow-2xl z-50 flex flex-col border-l border-groww-gray/10 transform transition-transform duration-300 ease-in-out ${
                    isOpen ? 'translate-x-0' : 'translate-x-full'
                }`}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-5 border-b border-groww-gray/10 bg-groww-light-gray/30 shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-groww-green/10 flex items-center justify-center text-groww-green">
                            <Bot size={22} />
                        </div>
                        <div>
                            <h2 className="font-bold text-groww-dark">Sentinel Copilot</h2>
                            <p className="text-xs text-groww-green font-semibold flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-groww-green animate-pulse inline-block" />
                                Neural Core Online
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="text-groww-gray hover:text-groww-dark hover:bg-groww-light-gray p-2 rounded-lg transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[85%] gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                                        msg.role === 'user' ? 'bg-groww-gray text-white' : 'bg-groww-green text-white'
                                    }`}
                                >
                                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                                </div>

                                <div
                                    className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                                        msg.role === 'user'
                                            ? 'bg-groww-green text-white rounded-tr-none'
                                            : 'bg-dark-card text-groww-dark rounded-tl-none border border-groww-gray/5'
                                    }`}
                                >
                                    {msg.role === 'agent' ? (
                                        <ReactMarkdown components={agentMarkdownComponents}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    ) : (
                                        msg.content
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Quick Prompt Chips — shown only on fresh conversation */}
                    {isFirstMessage && !isTyping && (
                        <div className="flex flex-col gap-2.5 pt-1">
                            <p className="text-xs text-groww-gray font-medium flex items-center gap-1.5">
                                <Zap size={12} className="text-groww-green" />
                                Quick prompts
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {QUICK_PROMPTS.map((prompt) => (
                                    <button
                                        key={prompt}
                                        onClick={() => sendMessage(prompt)}
                                        className="px-3 py-1.5 bg-dark-card border border-groww-green/40 text-groww-green text-xs rounded-full hover:bg-groww-green hover:text-white transition-all font-medium shadow-sm"
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Typing Indicator */}
                    {isTyping && (
                        <div className="flex justify-start">
                            <div className="flex gap-2">
                                <div className="w-8 h-8 rounded-full bg-groww-green text-white flex items-center justify-center shrink-0 mt-1">
                                    <Bot size={16} />
                                </div>
                                <div className="p-4 rounded-2xl rounded-tl-none bg-dark-card flex items-center gap-1.5 h-12">
                                    <span className="w-2 h-2 bg-groww-gray/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-2 h-2 bg-groww-gray/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-2 h-2 bg-groww-gray/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-groww-gray/10 bg-dark-bg shrink-0">
                    <div className="relative flex items-center">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Ask Sentinel about recent trades..."
                            className="w-full pl-4 pr-12 py-3 bg-groww-light-gray/50 border border-groww-gray/20 rounded-xl focus:outline-none focus:border-groww-green focus:bg-dark-bg transition-colors text-groww-dark placeholder-groww-gray text-sm"
                        />
                        <button
                            onClick={() => sendMessage()}
                            disabled={!input.trim() || isTyping}
                            className="absolute right-2 p-2 bg-groww-green text-white rounded-lg hover:bg-[#00b386] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
