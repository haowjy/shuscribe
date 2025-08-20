# TODO: API Integration Roadmap

**WHY THIS FILE EXISTS**: This document consolidates all the massive TODOs scattered across the data hooks. When backend APIs are implemented, this serves as the comprehensive integration guide for upgrading from localStorage-first to full client-server architecture with conflict resolution.

## 🎯 Current State: localStorage-First Architecture

✅ **IMPLEMENTED:**
- TanStack Query infrastructure with QueryClient provider
- Complete CRUD hooks for Projects, Documents, FileTree, Tags
- Optimistic updates for instant UI feedback
- Cache management and invalidation strategies
- Type-safe integration with existing Dexie database
- Component integration (studio page, file tree explorer)

## 🚀 Phase 1: Basic API Integration

### 1.1 Server Verification Pattern
**WHY**: Enable gradual migration from localStorage-only to hybrid local+server architecture.

**Implementation in each hook:**
```typescript
// Current: Return cached data immediately
const cached = await localProvider.getData()

// TODO: Add background server verification
const serverData = await apiClient.getData() // Background fetch
const resolved = resolveConflicts(cached, serverData)
return resolved
```

**Files to update:**
- `useProjects.ts` - GET /api/projects verification
- `useDocuments.ts` - GET /api/documents/{id} verification  
- `useFileTree.ts` - GET /api/projects/{id}/filetree verification
- `useTags.ts` - GET /api/projects/{id}/tags verification

### 1.2 Basic Conflict Detection
**WHY**: Detect when local and server data are out of sync.

**Strategy:**
- Compare `updatedAt` timestamps
- Compare `version` fields for documents
- Log conflicts for analysis before implementing resolution

## 🔄 Phase 2: Conflict Resolution

### 2.1 Timestamp-Based Resolution (Recommended for ShuScribe)
**WHY**: Simple, predictable resolution for most content types.

**Rules:**
- **Metadata conflicts**: Take server version (word counts, etc.)
- **User preferences**: Take local version (UI settings)
- **Content conflicts**: Prompt user for resolution

### 2.2 Document Content Conflicts
**WHY**: Writers need control over creative content conflicts.

**Implementation:**
- Three-way merge for compatible changes
- User-prompted resolution UI for content conflicts
- Operational transforms for real-time collaboration (future)

### 2.3 File Tree Structure Conflicts
**WHY**: File operations (rename, move) can conflict across users.

**Implementation:**
- Path conflict detection and resolution
- Cascade updates for folder operations
- Maintain referential integrity with documents

## 📡 Phase 3: Real-Time Synchronization

### 3.1 WebSocket Integration
**WHY**: Enable live collaboration and real-time updates.

**Features:**
- Live document updates during editing
- Real-time file tree changes
- User presence indicators
- Live cursor positions (advanced)

### 3.2 Offline Operation Queue
**WHY**: Robust offline support for creative work.

**Implementation:**
```typescript
interface SyncOperation {
  id: string
  type: 'create' | 'update' | 'delete'
  entity: 'project' | 'document' | 'fileTree' | 'tag'
  data: any
  timestamp: number
  retryCount: number
  userId: string
}
```

**Queue Management:**
- Store operations in Dexie during offline periods
- Automatic sync when connection restored
- Exponential backoff for failed requests
- Conflict resolution for queued operations

## 🎛️ Phase 4: Advanced Features

### 4.1 Collaborative Editing
**WHY**: Enable team-based content creation.

**Technologies:**
- Operational Transforms (OT) or Conflict-free Replicated Data Types (CRDTs)
- Real-time presence awareness
- Live cursor tracking
- Change attribution and history

### 4.2 Performance Optimizations
**WHY**: Maintain instant UI responsiveness even with server sync.

**Strategies:**
- Intelligent prefetching based on user patterns
- Delta compression for large documents
- Background sync prioritization
- Memory management for large datasets

### 4.3 Cross-Document Features
**WHY**: Support ShuScribe's @-reference system and content relationships.

**Features:**
- @-reference validation across server and local data
- Dependency tracking between documents
- Bulk operations with consistency guarantees
- Search across all content with real-time indexing

## 🔧 Implementation Guidelines

### Hook Update Pattern
Each data hook follows this pattern for API integration:

```typescript
export function useEntity(id: string) {
  // 1. IMMEDIATE RESPONSE: Return cached data from Dexie
  const cachedQuery = useQuery({
    queryKey: ['entity', id],
    queryFn: () => localProvider.getEntity(id),
    staleTime: 5 * 60 * 1000, // Trust cache for 5 minutes
  })

  // 2. BACKGROUND VERIFICATION: Fetch from server (when APIs ready)
  const serverQuery = useQuery({
    queryKey: ['entity-server', id],
    queryFn: () => apiClient.getEntity(id),
    enabled: !!cachedQuery.data, // Only after cache loads
    staleTime: 30 * 1000, // Check server every 30 seconds
  })

  // 3. CONFLICT RESOLUTION: Merge local and server data
  const resolvedData = useMemo(() => {
    if (!cachedQuery.data || !serverQuery.data) {
      return cachedQuery.data // Return cache if server not ready
    }
    
    return resolveConflicts(cachedQuery.data, serverQuery.data)
  }, [cachedQuery.data, serverQuery.data])

  return {
    data: resolvedData,
    isLoading: cachedQuery.isLoading,
    isStale: serverQuery.isStale,
    hasConflict: detectConflict(cachedQuery.data, serverQuery.data)
  }
}
```

### Mutation Update Pattern
```typescript
export function useUpdateEntity() {
  return useMutation({
    mutationFn: async (updates) => {
      // 1. IMMEDIATE UPDATE: Update Dexie cache
      const updated = await localProvider.updateEntity(updates)
      
      // 2. QUEUE FOR SYNC: Add to offline operation queue
      await syncQueue.add({
        type: 'update',
        entity: 'entity',
        data: updates,
        timestamp: Date.now()
      })
      
      // 3. BACKGROUND SYNC: Send to server when online
      if (navigator.onLine) {
        try {
          await apiClient.updateEntity(updates)
          await syncQueue.remove(operationId)
        } catch (error) {
          // Handle sync failure, keep in queue for retry
        }
      }
      
      return updated
    },
    onMutate: async (updates) => {
      // OPTIMISTIC UPDATE: Update cache immediately
      const previous = queryClient.getQueryData(['entity', id])
      queryClient.setQueryData(['entity', id], { ...previous, ...updates })
      return { previous }
    },
    onError: (error, updates, context) => {
      // ROLLBACK: Restore previous state on error
      if (context?.previous) {
        queryClient.setQueryData(['entity', id], context.previous)
      }
    }
  })
}
```

## 📋 Implementation Checklist

### Phase 1: Basic API Integration
- [ ] Add API client infrastructure
- [ ] Implement server verification in each hook
- [ ] Add conflict detection logging
- [ ] Create basic error handling

### Phase 2: Conflict Resolution
- [ ] Implement timestamp-based resolution
- [ ] Create conflict resolution UI components
- [ ] Add three-way merge for documents
- [ ] Test conflict scenarios

### Phase 3: Real-Time Sync
- [ ] Implement WebSocket connection
- [ ] Create offline operation queue
- [ ] Add automatic sync on reconnect
- [ ] Handle concurrent operations

### Phase 4: Advanced Features
- [ ] Add collaborative editing (OT/CRDT)
- [ ] Implement performance optimizations
- [ ] Create cross-document features
- [ ] Add comprehensive monitoring

## 🎨 UI/UX Considerations

### Conflict Resolution Interface
- **Silent Resolution**: For metadata and non-critical changes
- **User Prompt**: For content conflicts with clear options
- **Diff View**: Visual comparison for document changes
- **Merge Tools**: Manual merge assistance for complex conflicts

### Status Indicators
- **Sync Status**: Show when data is syncing or conflicts exist
- **Offline Mode**: Clear indication when working offline
- **Conflict Badge**: Visual indicators for items with conflicts
- **Real-Time Status**: Live updates and presence indicators

### Performance Feedback
- **Instant Updates**: Maintain zero-latency feel even with server sync
- **Background Operations**: Show sync progress without blocking UI
- **Error Recovery**: Graceful handling of sync failures
- **Loading States**: Appropriate indicators for network operations

---

**This roadmap ensures ShuScribe maintains its instant, creative-flow-friendly UX while adding robust server synchronization and collaboration features when backend APIs are ready.**