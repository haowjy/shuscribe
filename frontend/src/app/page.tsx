"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { WorkspaceLayout } from "@/components/layout/workspace-layout";
import { FileExplorer } from "@/components/layout/file-explorer";
import { EditorPlaceholder } from "@/components/layout/editor-placeholder";
import { AiPanel } from "@/components/layout/ai-panel";

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project");

  useEffect(() => {
    // If no project is selected, redirect to dashboard
    if (!projectId) {
      router.push("/dashboard");
      return;
    }

    // TODO: Load project data based on projectId
    // For now, just show the workspace
  }, [projectId, router]);

  return (
    <WorkspaceLayout
      projectId={projectId}
      fileExplorer={<FileExplorer />}
      editor={<EditorPlaceholder />}
      aiPanel={<AiPanel />}
    />
  );
}