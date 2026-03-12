import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { ArrowLeft, Activity, ShieldCheck, LineChart } from 'lucide-react';
import { BASE_URL } from './api';

export default function Analyze() {
    const { ticker } = useParams();
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        fetch(`${BASE_URL}/api/market/analyze/${ticker}`)
            .then(res => {
                if (!res.ok) throw new Error("Failed to generate Neural Analysis payload");
                return res.json();
            })
            .then(data => {
                setAnalysis(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setError(err.message);
                setLoading(false);
            });
    }, [ticker]);

    if (loading) {
        return (
            <div className="min-h-screen bg-groww-light-gray p-6 lg:p-10 font-sans">
                <button onClick={() => navigate(-1)} className="mb-6 flex items-center text-groww-gray hover:text-groww-dark font-bold transition-colors">
                    <ArrowLeft size={20} className="mr-2" /> Back to Discover
                </button>
                <div className="max-w-4xl mx-auto bg-dark-card rounded-2xl border border-groww-gray/20 p-8 shadow-sm">
                    <div className="flex flex-col items-center justify-center py-32">
                        <Activity className="animate-spin text-groww-green mb-6" size={48} />
                        <h2 className="text-xl font-bold text-groww-dark">Agentic Deep Dive in Progress</h2>
                        <p className="text-groww-gray mt-2 text-center max-w-md">
                            Neural Core is currently scanning 6 months of historical technical data and synthesizing a comprehensive fundamental report for <span className="font-bold text-groww-dark">{ticker}</span>...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    if (error || !analysis) {
        return (
            <div className="min-h-screen bg-groww-light-gray p-6 lg:p-10 font-sans flex flex-col items-center justify-center text-center">
                <div className="bg-groww-red/10 text-groww-red p-6 rounded-full mb-6">
                    <Activity size={48} />
                </div>
                <h2 className="text-3xl font-bold text-groww-dark">Analysis Failed</h2>
                <p className="text-groww-gray mt-3 mb-8 text-lg">{error || "Could not retrieve agentic analysis data."}</p>
                <button onClick={() => navigate(-1)} className="bg-groww-dark text-white px-8 py-3 rounded-lg font-bold hover:bg-black transition-colors">
                    Return to Discovery
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-groww-light-gray p-6 lg:p-10 font-sans">
            <div className="max-w-4xl mx-auto">
                {/* Back Button */}
                <button onClick={() => navigate(-1)} className="mb-6 flex items-center text-groww-gray hover:text-groww-dark font-bold transition-colors">
                    <ArrowLeft size={20} className="mr-2" /> Back to Discover
                </button>

                <div className="bg-dark-card rounded-2xl border border-groww-gray/20 overflow-hidden shadow-sm">

                    {/* Header Banner */}
                    <div className="p-8 border-b border-groww-gray/10 bg-gradient-to-r from-black to-groww-light-gray/40">
                        <div className="flex flex-col md:flex-row justify-between md:items-start gap-4">
                            <div>
                                <div className="flex items-center mb-2">
                                    <h1 className="text-4xl font-bold text-groww-dark tracking-tight mr-4">{analysis.ticker}</h1>
                                    <div className="bg-groww-green/10 text-groww-green px-3 py-1.5 rounded-full text-xs font-bold flex items-center uppercase tracking-wider">
                                        <ShieldCheck size={14} className="mr-1.5" /> Neural Verified
                                    </div>
                                </div>
                                <p className="text-lg text-groww-gray">{analysis.name}</p>
                            </div>

                            <div className="text-left md:text-right bg-dark-card md:bg-transparent p-4 md:p-0 rounded-xl border md:border-none border-groww-gray/10 shadow-sm md:shadow-none">
                                <p className="text-sm font-bold text-groww-gray mb-1 uppercase tracking-wider">Current Price</p>
                                <p className="text-3xl font-mono font-bold text-groww-dark">₹{analysis.current_price.toLocaleString()}</p>
                            </div>
                        </div>

                        {/* Fast Metadata Pills */}
                        <div className="mt-8 flex flex-wrap gap-4">
                            <div className="flex items-center text-sm font-bold text-groww-dark bg-dark-card border border-groww-gray/10 shadow-sm px-4 py-2.5 rounded-lg">
                                <LineChart size={18} className="text-groww-gray mr-2.5" />
                                20-Day SMA: <span className="font-mono ml-2 text-groww-green">₹{analysis.sma_20.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>

                    {/* Markdown Report Body */}
                    <div className="p-8 md:p-12">
                        <ReactMarkdown
                            components={{
                                h1: ({ node, ...props }) => <h1 className="text-2xl font-bold border-b-2 border-groww-green pb-3 inline-block mb-8 mt-2 tracking-tight text-groww-dark" {...props} />,
                                h2: ({ node, ...props }) => <h2 className="text-xl font-bold mt-10 mb-5 text-groww-dark flex items-center before:content-[''] before:w-2 before:h-2 before:bg-groww-green before:rounded-full before:mr-3" {...props} />,
                                h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-8 mb-4 text-groww-dark" {...props} />,
                                p: ({ node, ...props }) => <p className="text-groww-dark/80 leading-relaxed mb-6 text-base" {...props} />,
                                ul: ({ node, ...props }) => <ul className="list-disc pl-6 mb-6 text-groww-dark/80 space-y-2 marker:text-groww-green" {...props} />,
                                ol: ({ node, ...props }) => <ol className="list-decimal pl-6 mb-6 text-groww-dark/80 space-y-2 marker:text-groww-green font-bold" {...props} />,
                                li: ({ node, ...props }) => <li className="" {...props} />,
                                strong: ({ node, ...props }) => <strong className="font-bold text-groww-dark" {...props} />,
                                a: ({ node, ...props }) => <a className="text-groww-green hover:underline cursor-pointer" {...props} />,
                                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-groww-green pl-4 italic text-groww-gray my-6 bg-groww-light-gray/50 py-2 pr-2 rounded-r-lg" {...props} />
                            }}
                        >
                            {analysis.report}
                        </ReactMarkdown>
                    </div>

                </div>
            </div>
        </div>
    );
}
