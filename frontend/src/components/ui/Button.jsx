import React from 'react';

const variants = {
    primary: 'bg-accent-green text-dark-card hover:bg-accent-green/90 shadow-lg shadow-accent-green/20',
    secondary: 'bg-dark-card text-dark-text border border-dark-border hover:bg-dark-hover',
    danger: 'bg-accent-red/10 text-accent-red border border-accent-red/20 hover:bg-accent-red hover:text-white',
    ghost: 'text-dark-muted hover:text-dark-text hover:bg-dark-hover',
};

const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3.5 text-sm',
};

export default function Button({ children, variant = 'primary', size = 'md', className = '', disabled, ...props }) {
    return (
        <button
            className={`inline-flex items-center justify-center font-bold rounded-xl transition-all duration-200
                ${variants[variant]} ${sizes[size]}
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                ${className}`}
            disabled={disabled}
            {...props}
        >
            {children}
        </button>
    );
}
