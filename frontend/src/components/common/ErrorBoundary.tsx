import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback: React.ComponentType<{ error: Error; resetError: () => void }>;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError && this.state.error) {
      const { fallback }: { fallback: React.ComponentType<{ error: Error; resetError: () => void }> } =
        this.props;
      return <fallback error={this.state.error} resetError={this.resetError} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;