import React from 'react';

export default function Card({ children, className = '', hover = false, ...props }) {
    return (
        <div
            className={`bg-dark-card rounded-2xl border border-dark-border shadow-sm
                ${hover ? 'hover:border-accent-green/30 hover:shadow-md hover:shadow-accent-green/5 transition-all duration-300' : ''}
                ${className}`}
            {...props}
        >
            {children}
        </div>
    );
}

export function CardHeader({ children, className = '' }) {
    return (
        <div className={`px-6 pt-5 pb-3 ${className}`}>
            {children}
        </div>
    );
}

export function CardContent({ children, className = '' }) {
    return (
        <div className={`px-6 pb-5 ${className}`}>
            {children}
        </div>
    );
}
