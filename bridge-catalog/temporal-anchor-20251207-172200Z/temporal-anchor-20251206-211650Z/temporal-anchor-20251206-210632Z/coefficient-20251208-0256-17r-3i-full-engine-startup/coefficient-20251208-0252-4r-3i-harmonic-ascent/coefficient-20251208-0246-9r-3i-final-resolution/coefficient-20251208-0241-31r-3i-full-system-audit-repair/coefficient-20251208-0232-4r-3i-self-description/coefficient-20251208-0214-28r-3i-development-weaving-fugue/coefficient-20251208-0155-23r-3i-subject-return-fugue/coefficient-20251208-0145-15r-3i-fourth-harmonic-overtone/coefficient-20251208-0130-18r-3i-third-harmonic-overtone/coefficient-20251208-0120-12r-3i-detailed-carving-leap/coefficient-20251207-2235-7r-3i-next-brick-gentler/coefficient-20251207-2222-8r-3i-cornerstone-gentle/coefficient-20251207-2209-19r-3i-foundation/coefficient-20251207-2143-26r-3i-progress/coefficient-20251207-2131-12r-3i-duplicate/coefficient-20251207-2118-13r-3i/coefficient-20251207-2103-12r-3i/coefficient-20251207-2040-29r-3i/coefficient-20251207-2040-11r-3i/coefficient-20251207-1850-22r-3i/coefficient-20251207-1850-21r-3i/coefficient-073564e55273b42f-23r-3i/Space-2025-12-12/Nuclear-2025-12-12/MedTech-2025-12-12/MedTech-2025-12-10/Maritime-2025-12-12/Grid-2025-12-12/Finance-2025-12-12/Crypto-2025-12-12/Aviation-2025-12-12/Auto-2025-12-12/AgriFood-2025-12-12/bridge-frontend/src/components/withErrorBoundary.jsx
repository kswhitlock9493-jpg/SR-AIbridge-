import ErrorBoundary from './ErrorBoundary';

/**
 * Higher-order component to wrap components with error boundary
 */
export function withErrorBoundary(Component, options = {}) {
  const WrappedComponent = (props) => (
    <ErrorBoundary
      name={options.name || Component.name || 'Component'}
      fallback={options.fallback}
      onError={options.onError}
      onReset={options.onReset}
      errorMessage={options.errorMessage}
      degradedContent={options.degradedContent}
      showDetails={options.showDetails !== false}
    >
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.name || 'Component'})`;
  return WrappedComponent;
}
