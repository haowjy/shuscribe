"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { WorkspaceLayout } from "@/components/layout/workspace-layout";

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project");

  useEffect(() => {
    // If no project is selected, redirect to dashboard for project selection
    if (!projectId) {
      router.replace("/dashboard");
      return;
    }

    // TODO: Validate project exists and user has access
    // For now, just show the workspace if projectId is provided
  }, [projectId, router]);

  // Show loading while redirecting to dashboard
  if (!projectId) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return <WorkspaceLayout projectId={projectId} />;
}