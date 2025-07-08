"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { storage } from "@/lib/storage";

export default function TestStoragePage() {
  const [stats, setStats] = useState(storage.getStorageStats());
  const [testData, setTestData] = useState<string | null>(null);

  const refreshStats = () => {
    setStats(storage.getStorageStats());
  };

  const testSave = () => {
    const data = { message: "Hello from localStorage!", timestamp: Date.now() };
    const success = storage.set("test-data", data, "test-project");
    if (success) {
      setTestData(JSON.stringify(data, null, 2));
    }
    refreshStats();
  };

  const testLoad = () => {
    const data = storage.get("test-data", "test-project");
    setTestData(data ? JSON.stringify(data, null, 2) : "No data found");
  };

  const testClear = () => {
    storage.clearProject("test-project");
    setTestData(null);
    refreshStats();
  };

  const testCleanup = () => {
    storage.cleanup(0); // Clean up all data
    refreshStats();
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>localStorage Test Page</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button onClick={testSave}>Save Test Data</Button>
              <Button onClick={testLoad} variant="outline">Load Test Data</Button>
              <Button onClick={testClear} variant="destructive">Clear Project Data</Button>
              <Button onClick={testCleanup} variant="destructive">Cleanup All</Button>
              <Button onClick={refreshStats} variant="secondary">Refresh Stats</Button>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Storage Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div>Used: {stats.usedMB} MB / {stats.maxMB} MB</div>
                  <div>Percentage: {stats.percentage}%</div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(stats.percentage, 100)}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {testData && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Test Data</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-xs bg-secondary p-2 rounded overflow-auto">
                    {testData}
                  </pre>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}