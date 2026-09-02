import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, retryCount: 0 };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('[ErrorBoundary]', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="flex flex-col items-center justify-center min-h-[300px] p-8 bg-dark-card rounded-xl border border-dark-border">
                    <AlertTriangle className="w-12 h-12 text-accent-red mb-4" />
                    <h2 className="text-lg font-bold text-dark-text mb-2">Something went wrong</h2>
                    <p className="text-dark-muted text-sm mb-4 text-center max-w-md">
                        {this.props.fallbackMessage || 'An unexpected error occurred in this section.'}
                    </p>
                    <button
                        onClick={() => this.setState((state) => ({ hasError: false, error: null, retryCount: state.retryCount + 1 }))}
                        className="flex items-center gap-2 px-4 py-2 bg-accent-green/10 text-accent-green rounded-lg hover:bg-accent-green/20 transition-colors"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Try Again
                    </button>
                </div>
            );
        }
        return <React.Fragment key={this.state.retryCount}>{this.props.children}</React.Fragment>;
    }
}
