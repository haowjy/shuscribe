import debug from 'debug';

/**
 * Creates a debug logger with the given namespace
 * Usage: const debugComponent = createDebug('app:component:MyComponent')
 * 
 * To enable debug output in development:
 * - Browser console: localStorage.debug = 'app:*'
 * - Or specific: localStorage.debug = 'app:component:*'
 * 
 * Debug logs are automatically disabled in production unless explicitly enabled
 */
export const createDebug = (namespace: string) => debug(namespace);

/**
 * Pre-configured debug loggers for common use cases
 */
export const debuggers = {
  component: createDebug('app:component'),
  api: createDebug('app:api'),
  storage: createDebug('app:storage'),
  hooks: createDebug('app:hooks'),
  editor: createDebug('app:editor'),
  auth: createDebug('app:auth'),
  performance: createDebug('app:performance'),
};

/**
 * Utility function to enable all debug logs (for development)
 */
export const enableAllDebugLogs = () => {
  if (typeof window !== 'undefined') {
    localStorage.debug = 'app:*';
  }
};

/**
 * Utility function to disable all debug logs
 */
export const disableAllDebugLogs = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('debug');
  }
};