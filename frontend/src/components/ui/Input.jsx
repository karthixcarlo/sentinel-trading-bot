import React from 'react';

export default function Input({ label, className = '', ...props }) {
    return (
        <div className="space-y-1.5">
            {label && <label className="text-xs font-bold text-dark-muted uppercase tracking-wider">{label}</label>}
            <input
                className={`w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-2.5 text-sm text-dark-text
                    placeholder:text-dark-muted/50 focus:outline-none focus:border-accent-green/50 focus:ring-1 focus:ring-accent-green/20
                    transition-colors duration-200 ${className}`}
                {...props}
            />
        </div>
    );
}
