export const CONFIG = {
  APP_NAME: 'Thirukkural Educational AI',
  APP_VERSION: '1.0.0',
  API_URL:
    import.meta.env.VITE_API_URL ||
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8000'
      : ''),
};

// Validate configuration in development
if (import.meta.env.DEV) {
  if (!CONFIG.API_URL) {
    console.warn('VITE_API_URL is not set, falling back to default');
  }

  // Log configuration (excluding sensitive data)
  console.log('Application Configuration:', {
    appName: CONFIG.APP_NAME,
    appVersion: CONFIG.APP_VERSION,
    apiUrl: CONFIG.API_URL
  });
}