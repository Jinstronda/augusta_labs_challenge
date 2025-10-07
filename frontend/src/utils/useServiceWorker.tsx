/**
 * Service Worker Registration Hook
 * 
 * Handles service worker registration and updates for PWA functionality.
 * Provides offline support and caching strategies.
 * 
 * This is a simplified version that works without the virtual:pwa-register module.
 * The vite-plugin-pwa will automatically generate and register the service worker.
 * 
 * Usage:
 * ```
 * import { useServiceWorker } from './utils/useServiceWorker';
 * 
 * function App() {
 *   const { needRefresh, updateServiceWorker } = useServiceWorker();
 *   
 *   if (needRefresh) {
 *     return <UpdateNotification />;
 *   }
 *   
 *   return <YourApp />;
 * }
 * ```
 */

import { useEffect, useState } from 'react';

export interface ServiceWorkerState {
  /** Whether a new version is available */
  needRefresh: boolean;
  /** Whether the service worker is being updated */
  updating: boolean;
  /** Function to trigger service worker update */
  updateServiceWorker: () => void;
  /** Whether offline mode is active */
  offlineReady: boolean;
}

/**
 * Hook for managing service worker registration and updates
 * 
 * This is a simplified implementation that works with vite-plugin-pwa's
 * automatic service worker registration. The plugin handles registration
 * automatically, and this hook provides UI state management.
 */
export function useServiceWorker(): ServiceWorkerState {
  const [needRefresh, setNeedRefresh] = useState(false);
  const [offlineReady, setOfflineReady] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    // Check if service worker is supported
    if (!('serviceWorker' in navigator)) {
      return;
    }

    // Listen for service worker updates
    navigator.serviceWorker.ready.then((registration) => {
      console.log('[SW] Service worker ready');
      setOfflineReady(true);

      // Check for updates periodically
      const checkForUpdates = () => {
        registration.update().catch((error) => {
          console.error('[SW] Update check failed:', error);
        });
      };

      // Check for updates every hour
      const intervalId = setInterval(checkForUpdates, 60 * 60 * 1000);

      // Listen for new service worker waiting
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('[SW] New version available');
              setNeedRefresh(true);
            }
          });
        }
      });

      return () => clearInterval(intervalId);
    });

    // Listen for controller change (new service worker activated)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('[SW] Controller changed, reloading...');
      window.location.reload();
    });
  }, []);

  const updateServiceWorker = async () => {
    setUpdating(true);
    try {
      // Tell the service worker to skip waiting and activate
      const registration = await navigator.serviceWorker.ready;
      if (registration.waiting) {
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      }
      // The controllerchange event will trigger a reload
    } catch (error) {
      console.error('[SW] Failed to update service worker:', error);
      setUpdating(false);
      // Fallback: just reload
      window.location.reload();
    }
  };

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      console.log('[SW] Back online');
    };

    const handleOffline = () => {
      console.log('[SW] Gone offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return {
    needRefresh,
    updating,
    updateServiceWorker,
    offlineReady,
  };
}

/**
 * Update notification component
 * 
 * Shows a banner when a new version is available
 */
export function UpdateNotification() {
  const { needRefresh, updating, updateServiceWorker, offlineReady } = useServiceWorker();

  if (offlineReady && !needRefresh) {
    return (
      <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg">
        <p className="text-sm font-medium">App ready to work offline</p>
      </div>
    );
  }

  if (!needRefresh) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-6 py-4 rounded-lg shadow-lg max-w-sm">
      <div className="flex items-start gap-3">
        <svg
          className="w-6 h-6 flex-shrink-0 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        <div className="flex-1">
          <p className="font-semibold mb-1">New Version Available</p>
          <p className="text-sm text-blue-100 mb-3">
            A new version of the app is ready. Click update to get the latest features.
          </p>
          <button
            onClick={updateServiceWorker}
            disabled={updating}
            className="bg-white text-blue-600 px-4 py-2 rounded font-medium text-sm hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updating ? 'Updating...' : 'Update Now'}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Offline indicator component
 * 
 * Shows when the app is offline
 */
export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-white px-4 py-2 text-center z-50">
      <div className="flex items-center justify-center gap-2">
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
          />
        </svg>
        <span className="font-medium">You're offline. Some features may be limited.</span>
      </div>
    </div>
  );
}
