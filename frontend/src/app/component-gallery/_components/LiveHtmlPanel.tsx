interface LiveHtmlPanelProps {
  content: string;
}

export default function LiveHtmlPanel({ content }: LiveHtmlPanelProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <h3 className="font-semibold mb-3">Live HTML Output</h3>
      <div className="bg-muted rounded p-3 max-h-60 overflow-y-auto">
        <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
          {content || "No content yet... Start typing in the editor to see the HTML output here."}
        </pre>
      </div>
    </div>
  );
}