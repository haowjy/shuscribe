"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { WorkspaceLayout } from "@/components/layout/workspace-layout";
import { FileExplorer } from "@/components/layout/file-explorer";
import { EditorWorkspace } from "@/components/layout/editor-workspace";
import { AiPanel } from "@/components/layout/ai-panel";

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project") || "prj_fantasy_novel";

  useEffect(() => {
    // If no project is selected, set default project instead of redirecting
    if (!searchParams.get("project")) {
      // Use URL replace to set default project without triggering navigation
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set("project", "prj_fantasy_novel");
      window.history.replaceState({}, "", newUrl.toString());
      return;
    }

    // TODO: Load project data based on projectId
    // For now, just show the workspace
  }, [searchParams, router]);

  return (
    <WorkspaceLayout
      projectId={projectId}
      fileExplorer={<FileExplorer projectId={projectId} />}
      editor={<EditorWorkspace projectId={projectId} />}
      aiPanel={<AiPanel />}
    />
  );
}