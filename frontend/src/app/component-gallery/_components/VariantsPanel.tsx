export default function VariantsPanel() {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <h3 className="font-semibold mb-3">Editor Variants</h3>
      <div className="text-sm space-y-2">
        <div>📝 <strong>Full Editor:</strong> All features enabled</div>
        <div>💬 <strong>Chat Editor:</strong> Basic formatting only</div>
        <div>📄 <strong>Notes Editor:</strong> Minimal toolbar</div>
        <div>🎯 <strong>Custom:</strong> Use hooks for complete control</div>
      </div>
    </div>
  );
}