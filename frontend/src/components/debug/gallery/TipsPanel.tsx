export default function TipsPanel() {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <h3 className="font-semibold mb-3">Quick Tips</h3>
      <div className="text-sm space-y-2 text-muted-foreground">
        <div>• Use toolbar buttons for all formatting</div>
        <div>• Active formatting shows highlighted buttons</div>
        <div>• Try task lists with checkboxes</div>
        <div>• Insert tables with resizable columns</div>
        <div>• Text alignment works on headings too</div>
        <div>• Link/image prompts for URLs</div>
        <div>• Character count updates live</div>
        <div>• All keyboard shortcuts still work!</div>
      </div>
    </div>
  );
}