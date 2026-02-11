import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
    children?: ReactNode
}

interface State {
    hasError: boolean
    error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo)
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    height: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-body)',
                    padding: '2rem',
                    textAlign: 'center'
                }}>
                    <h1 className="t-display t-lg" style={{ color: 'var(--risk-high)', marginBottom: '1rem' }}>
                        System Error
                    </h1>
                    <p style={{ maxWidth: '500px', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                        The application encountered a critical error. Please reload the page.
                    </p>
                    <div style={{
                        background: 'var(--bg-card)',
                        padding: '1rem',
                        borderRadius: 'var(--radius)',
                        fontFamily: 'monospace',
                        fontSize: '0.8rem',
                        color: 'var(--risk-high)',
                        marginBottom: '2rem',
                        maxWidth: '100%',
                        overflow: 'auto'
                    }}>
                        {this.state.error?.toString()}
                    </div>
                    <button
                        onClick={() => window.location.reload()}
                        className="btn-accent"
                    >
                        Reload System
                    </button>
                </div>
            )
        }

        return this.props.children
    }
}
