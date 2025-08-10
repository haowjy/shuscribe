'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { clearAllLocalData, exportAllData, importAllData, getStorageStats } from '@/lib/localdb/admin';
import { seedSampleProject, seedLargeDemo } from '@/lib/localdb/seeds';
import { buildReferenceIndex, searchReferenceIndex, type ReferenceIndexEntry } from '@/lib/localdb/reference-index';
import { localDataProvider } from '@/lib/data/local-provider';

export default function StorageDebugPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [referenceIndex, setReferenceIndex] = useState<ReferenceIndexEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ReferenceIndexEntry[]>([]);

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (searchQuery && referenceIndex.length > 0) {
      const results = searchReferenceIndex(referenceIndex, searchQuery);
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery, referenceIndex]);

  const loadStats = async () => {
    try {
      const storageStats = await getStorageStats();
      setStats(storageStats);
      
      // Load first project for testing
      const projects = await localDataProvider.getProjects();
      if (projects.length > 0) {
        setCurrentProjectId(projects[0].id);
        const index = await buildReferenceIndex(projects[0].id);
        setReferenceIndex(index);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleAction = async (action: () => Promise<void | string>, successMessage: string) => {
    setIsLoading(true);
    setMessage('');
    try {
      const result = await action();
      if (typeof result === 'string') {
        setCurrentProjectId(result);
      }
      setMessage(successMessage);
      await loadStats(); // Refresh stats after action
    } catch (error: any) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await handleAction(
        () => importAllData(file),
        'Data imported successfully'
      );
      // Clear the file input
      e.target.value = '';
    }
  };

  const refreshIndex = async () => {
    if (!currentProjectId) return;
    
    setIsLoading(true);
    try {
      const index = await buildReferenceIndex(currentProjectId);
      setReferenceIndex(index);
      setMessage(`Reference index refreshed with ${index.length} entries`);
    } catch (error: any) {
      setMessage(`Error refreshing index: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Local Storage Debug Tools</h1>
        <div className="text-sm text-muted-foreground">
          IndexedDB Testing
        </div>
      </div>
      
      {message && (
        <div className={`p-3 rounded border ${
          message.startsWith('Error') 
            ? 'bg-destructive/10 text-destructive border-destructive/20' 
            : 'bg-muted border-border'
        }`}>
          {message}
        </div>
      )}

      {/* Storage Statistics */}
      {stats && (
        <div className="bg-muted/50 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">Storage Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
            <div>
              <div className="font-medium">Projects</div>
              <div className="text-2xl font-bold text-blue-600">{stats.projects}</div>
            </div>
            <div>
              <div className="font-medium">Documents</div>
              <div className="text-2xl font-bold text-green-600">{stats.documents}</div>
            </div>
            <div>
              <div className="font-medium">File Tree</div>
              <div className="text-2xl font-bold text-purple-600">{stats.fileTree}</div>
            </div>
            <div>
              <div className="font-medium">Tags</div>
              <div className="text-2xl font-bold text-orange-600">{stats.tags}</div>
            </div>
            <div>
              <div className="font-medium">Indexes</div>
              <div className="text-2xl font-bold text-pink-600">{stats.referenceIndex}</div>
            </div>
            <div>
              <div className="font-medium">Meta</div>
              <div className="text-2xl font-bold text-gray-600">{stats.meta}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Data Management */}
        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Data Management</h2>
          <div className="space-y-3">
            <Button
              onClick={() => handleAction(clearAllLocalData, 'All data cleared')}
              disabled={isLoading}
              variant="destructive"
              className="w-full"
            >
              Clear All Data
            </Button>
            
            <Button
              onClick={() => handleAction(seedSampleProject, 'Sample project created')}
              disabled={isLoading}
              className="w-full"
            >
              Seed Sample Project
            </Button>
            
            <Button
              onClick={() => handleAction(seedLargeDemo, 'Large demo created')}
              disabled={isLoading}
              className="w-full"
            >
              Seed Large Demo
            </Button>
          </div>
        </div>

        {/* Import/Export */}
        <div className="border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Import/Export</h2>
          <div className="space-y-3">
            <Button
              onClick={() => handleAction(exportAllData, 'Data exported to file')}
              disabled={isLoading}
              variant="outline"
              className="w-full"
            >
              Export Data (JSON)
            </Button>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Import Data:</label>
              <Input
                type="file"
                accept=".json"
                onChange={handleFileImport}
                disabled={isLoading}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Reference Index Testing */}
      <div className="border rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Reference Index Testing</h2>
          <Button
            onClick={refreshIndex}
            disabled={isLoading || !currentProjectId}
            variant="outline"
            size="sm"
          >
            Refresh Index
          </Button>
        </div>
        
        {currentProjectId ? (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Search References ({referenceIndex.length} entries):
              </label>
              <Input
                type="text"
                placeholder="Type to search references..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            
            {searchResults.length > 0 && (
              <div className="bg-muted/50 rounded-lg p-4 max-h-60 overflow-y-auto">
                <div className="text-sm font-medium mb-2">
                  Search Results ({searchResults.length}):
                </div>
                <div className="space-y-2">
                  {searchResults.map((entry, index) => (
                    <div key={index} className="bg-background p-2 rounded border">
                      <div className="font-medium">
                        <span className={`inline-block w-12 text-xs px-1 py-0.5 rounded mr-2 ${
                          entry.type === 'file' ? 'bg-blue-100 text-blue-800' :
                          entry.type === 'folder' ? 'bg-green-100 text-green-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {entry.type}
                        </span>
                        {entry.name}
                      </div>
                      {entry.path && (
                        <div className="text-sm text-muted-foreground mt-1">
                          {entry.path}
                        </div>
                      )}
                      {entry.description && (
                        <div className="text-xs text-muted-foreground mt-1">
                          {entry.description}
                        </div>
                      )}
                      {entry.tags && entry.tags.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {entry.tags.map(tag => (
                            <span key={tag} className="text-xs bg-gray-100 px-1 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-muted-foreground text-center py-8">
            No project available. Create a sample project to test the reference index.
          </div>
        )}
      </div>

    </div>
  );
}