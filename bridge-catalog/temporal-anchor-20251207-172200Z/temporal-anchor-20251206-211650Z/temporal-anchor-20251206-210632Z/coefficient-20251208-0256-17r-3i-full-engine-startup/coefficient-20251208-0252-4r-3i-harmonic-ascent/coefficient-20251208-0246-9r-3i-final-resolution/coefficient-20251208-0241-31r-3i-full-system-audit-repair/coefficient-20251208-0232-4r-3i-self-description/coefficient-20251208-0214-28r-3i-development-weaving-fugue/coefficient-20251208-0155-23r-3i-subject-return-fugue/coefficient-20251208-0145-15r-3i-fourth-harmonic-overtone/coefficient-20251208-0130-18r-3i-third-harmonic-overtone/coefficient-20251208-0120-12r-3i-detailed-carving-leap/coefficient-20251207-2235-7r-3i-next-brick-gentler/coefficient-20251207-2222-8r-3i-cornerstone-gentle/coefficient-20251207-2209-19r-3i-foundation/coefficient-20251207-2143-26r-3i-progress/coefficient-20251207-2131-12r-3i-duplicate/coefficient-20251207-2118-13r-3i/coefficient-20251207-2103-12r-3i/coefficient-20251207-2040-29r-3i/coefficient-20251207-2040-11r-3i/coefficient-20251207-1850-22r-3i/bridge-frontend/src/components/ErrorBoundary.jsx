import { Component } from 'react';
import { TriageEngine } from '../services/healing-net';

/**
 * Error Boundary Component - Healing Net Protection
 * Isolates component crashes to prevent cascade failures
 * Provides graceful degradation and recovery options
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
      lastError: null
    };
  }

  static getDerivedStateFromError(_error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    const errorData = {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      component: this.props.name || 'Unknown'
    };

    // Record in Triage Engine
    TriageEngine.recordDiagnostic({
      type: 'component_crash',
      component: this.props.name || 'Unknown',
      error: error.toString(),
      stack: errorInfo.componentStack,
      timestamp: errorData.timestamp
    });

    // Log to console
    console.error('[ErrorBoundary] Component crash detected:', errorData);

    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1,
      lastError: errorData.timestamp
    }));

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });

    // Call optional reset handler
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return typeof this.props.fallback === 'function'
          ? this.props.fallback(this.state.error, this.handleReset)
          : this.props.fallback;
      }

      // Default fallback UI
      const componentName = this.props.name || 'Component';
      
      return (
        <div className="error-boundary-fallback" style={{
          padding: '20px',
          margin: '20px 0',
          border: '2px solid #ff6b6b',
          borderRadius: '8px',
          backgroundColor: 'rgba(255, 107, 107, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '24px', marginRight: '8px' }}>⚠️</span>
            <h3 style={{ margin: 0, color: '#ff6b6b' }}>
              {componentName} Temporarily Unavailable
            </h3>
          </div>
          
          <p style={{ margin: '8px 0', color: '#666' }}>
            {this.props.errorMessage || 'This component encountered an error and has been isolated to prevent system-wide failures.'}
          </p>
          
          {this.state.errorCount > 1 && (
            <p style={{ margin: '8px 0', fontSize: '14px', color: '#999' }}>
              Error occurred {this.state.errorCount} times
            </p>
          )}

          <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
            <button
              onClick={this.handleReset}
              style={{
                padding: '8px 16px',
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🔄 Try Again
            </button>

            {this.props.showDetails && (
              <details style={{ marginTop: '8px' }}>
                <summary style={{ cursor: 'pointer', color: '#666' }}>
                  Show Error Details
                </summary>
                <pre style={{
                  marginTop: '8px',
                  padding: '12px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                  fontSize: '12px',
                  overflow: 'auto',
                  maxHeight: '200px'
                }}>
                  {this.state.error?.toString()}
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </div>

          {this.props.degradedContent && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: 'rgba(255, 255, 255, 0.5)',
              borderRadius: '4px'
            }}>
              <p style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>
                Degraded Mode Available:
              </p>
              {this.props.degradedContent}
            </div>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
