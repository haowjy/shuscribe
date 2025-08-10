export default function CustomizationPanel() {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <h3 className="font-semibold mb-3">Customization Features</h3>
      <div className="text-sm space-y-2">
        <div>✅ <strong>Toolbar Sections:</strong> Choose which sections to include (history, textStyle, formatting, lists, alignment, blocks, insert, table)</div>
        <div>✅ <strong>Individual Commands:</strong> Select specific commands to show (toggleBold, toggleItalic, etc.)</div>
        <div>✅ <strong>Footer Config:</strong> Toggle character count, word count, stats</div>
        <div>✅ <strong>Extension Overrides:</strong> Customize highlight, link, table behaviors</div>
        <div>✅ <strong>Composition Pattern:</strong> Use hooks and primitives for custom editors</div>
      </div>
    </div>
  );
}