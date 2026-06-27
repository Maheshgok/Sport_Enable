/**
 * Global Error Boundary
 * Catches React errors and displays a fallback UI
 */

import { Component } from 'react';
import { AlertCircle } from 'lucide-react';
import { errorLogger } from '../../utils/errorHandler';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Log to error tracking service
    errorLogger.log(error);

    // Log error info
    console.error('Error Boundary caught an error:', {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      const isDev = import.meta.env.VITE_ENV === 'development';

      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
            {/* Error Icon */}
            <div className="flex justify-center mb-6">
              <div className="bg-red-100 rounded-full p-4">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>

            {/* Error Message */}
            <p className="text-center text-gray-600 mb-6">
              We're sorry, but the application encountered an unexpected error.
              Our team has been notified.
            </p>

            {/* Error Details (Dev Only) */}
            {isDev && this.state.error && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6 max-h-48 overflow-y-auto">
                <h3 className="text-xs font-semibold text-gray-700 mb-2">
                  Error Details (Dev Mode)
                </h3>
                <p className="text-xs font-mono text-red-600 mb-2">
                  {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <details className="text-xs text-gray-600">
                    <summary className="cursor-pointer font-semibold mb-1">
                      Stack Trace
                    </summary>
                    <pre className="text-xs overflow-auto whitespace-pre-wrap">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={this.handleReset}
                className="w-full px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>

              <button
                onClick={this.handleReload}
                className="w-full px-4 py-2.5 bg-gray-200 text-gray-900 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Reload Page
              </button>

              <button
                onClick={this.handleGoHome}
                className="w-full px-4 py-2.5 bg-white text-gray-900 border-2 border-gray-300 rounded-lg font-medium hover:border-gray-400 transition-colors"
              >
                Go to Home
              </button>
            </div>

            {/* Support Info */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-center text-gray-500">
                Still having trouble?{' '}
                <a href="mailto:support@moove.ai" className="text-blue-600 hover:underline">
                  Contact Support
                </a>
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
