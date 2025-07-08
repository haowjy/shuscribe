import { WorkspaceLayout } from "@/components/layout/workspace-layout";
import { FileExplorer } from "@/components/layout/file-explorer";
import { EditorPlaceholder } from "@/components/layout/editor-placeholder";
import { AiPanel } from "@/components/layout/ai-panel";

export default function HomePage() {
  return (
    <WorkspaceLayout
      fileExplorer={<FileExplorer />}
      editor={<EditorPlaceholder />}
      aiPanel={<AiPanel />}
    />
  );
}