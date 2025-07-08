"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { WorkspaceLayout } from "@/components/layout/workspace-layout";
import { FileExplorer } from "@/components/layout/file-explorer";
import { EditorPlaceholder } from "@/components/layout/editor-placeholder";
import { AiPanel } from "@/components/layout/ai-panel";
import { FileItem } from "@/data/file-tree";

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project");
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);

  useEffect(() => {
    // If no project is selected, redirect to dashboard
    if (!projectId) {
      router.push("/dashboard");
      return;
    }

    // TODO: Load project data based on projectId
    // For now, just show the workspace
  }, [projectId, router]);

  const handleFileSelect = (file: FileItem) => {
    setSelectedFile(file);
  };

  return (
    <WorkspaceLayout
      projectId={projectId}
      fileExplorer={<FileExplorer onFileSelect={handleFileSelect} />}
      editor={<EditorPlaceholder selectedFile={selectedFile} projectId={projectId || "default"} />}
      aiPanel={<AiPanel />}
    />
  );
}