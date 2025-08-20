'use client'

/**
 * TanStack Query Provider - Client-side Data Management
 * 
 * WHY: This provider enables the localStorage-first + API verification architecture.
 * ShuScribe prioritizes instant UI responses from local cache (Dexie) while preparing
 * for background server synchronization when APIs are implemented.
 * 
 * Problem Context: Content creators need instant feedback when editing. Traditional
 * web apps wait for server responses, creating jarring delays. This provider enables
 * immediate local responses with future server sync capabilities.
 * 
 * Architecture Benefits:
 * - Instant UI updates from Dexie cache (zero latency)
 * - Optimistic updates for immediate user feedback
 * - Background sync preparation for conflict resolution
 * - Automatic cache invalidation and stale data handling
 * 
 * Integration Points:
 * - Works with existing LocalDataProvider for immediate migration
 * - Prepares for future API integration with conflict resolution
 * - Maintains compatibility with ProjectStateProvider
 * 
 * @see frontend/src/lib/data/local-provider.ts - Current data layer
 * @see frontend/src/hooks/data/ - Query hooks that use this provider
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ReactNode, useState } from 'react'

interface QueryProviderProps {
  children: ReactNode
}

export function QueryProvider({ children }: QueryProviderProps) {
  // Create QueryClient with optimized defaults for localStorage-first architecture
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Aggressive caching since we're localStorage-first
        staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh longer
        gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache longer
        
        // Background refetching settings (for future API integration)
        refetchOnWindowFocus: false, // Disable until APIs are ready
        refetchOnReconnect: false, // Disable until APIs are ready
        
        // Error handling
        retry: (failureCount, error) => {
          // Don't retry localStorage operations
          // TODO: When APIs are added, implement smart retry logic
          return false
        },
        
        // Performance optimization
        refetchOnMount: false, // Trust cache, localStorage is fast
      },
      mutations: {
        // Optimistic updates for instant UI feedback
        onMutate: async () => {
          // TODO: Implement optimistic update patterns when needed
        },
        
        onError: (error, variables, context) => {
          // TODO: Rollback optimistic updates on error
          console.error('Mutation error:', error)
        },
        
        onSuccess: () => {
          // TODO: Sync with server when APIs are available
        }
      }
    }
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      
      {/* Development tools - only in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false}
          buttonPosition="bottom-left"
        />
      )}
    </QueryClientProvider>
  )
}

/*
 * TODO: API VERIFICATION & CONFLICT RESOLUTION ARCHITECTURE
 * 
 * When backend APIs are implemented, this provider will coordinate:
 * 
 * 1. DUAL DATA STRATEGY:
 *    - Immediate response from Dexie cache
 *    - Background verification with server API
 *    - Conflict detection and resolution
 * 
 * 2. CONFLICT RESOLUTION PATTERNS:
 *    - Timestamp-based resolution for most conflicts
 *    - User-prompted resolution for content conflicts
 *    - Automatic merge for compatible changes
 * 
 * 3. SYNC QUEUE MANAGEMENT:
 *    - Queue offline operations for later sync
 *    - Retry failed API calls with exponential backoff
 *    - Handle network reconnection gracefully
 * 
 * 4. PERFORMANCE OPTIMIZATIONS:
 *    - Batch API calls to reduce network overhead
 *    - Smart cache invalidation based on server responses
 *    - Prefetch related data based on user patterns
 * 
 * 5. ERROR HANDLING:
 *    - Graceful degradation when server is unavailable
 *    - Clear user feedback for sync conflicts
 *    - Recovery strategies for corrupted local data
 */