"use client";

import { EditorState } from "prosemirror-state";
import { EditorView } from "prosemirror-view";
import { 
  Bold, 
  Italic, 
  Code,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Quote,
  AtSign
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { toggleMark, setBlockType, wrapIn } from "prosemirror-commands";
import { wrapInList, liftListItem, sinkListItem } from "prosemirror-schema-list";
import { cn } from "@/lib/utils";

interface EditorToolbarProps {
  editorView: EditorView | null;
  editorState: EditorState | null;
  className?: string;
}

interface ToolbarButtonProps {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  title: string;
}

function ToolbarButton({ onClick, isActive, disabled, children, title }: ToolbarButtonProps) {
  return (
    <Button
      variant={isActive ? "default" : "ghost"}
      size="sm"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={cn(
        "h-8 w-8 p-0",
        isActive && "bg-primary text-primary-foreground"
      )}
    >
      {children}
    </Button>
  );
}

export function EditorToolbar({ editorView, editorState, className }: EditorToolbarProps) {
  if (!editorView || !editorState) {
    return null;
  }

  const { schema } = editorState;
  const { selection } = editorState;

  // Check if a mark is active
  const isMarkActive = (markType: any) => {
    const { from, $from, to, empty } = selection;
    if (empty) {
      return markType.isInSet(editorState.storedMarks || $from.marks());
    }
    return editorState.doc.rangeHasMark(from, to, markType);
  };

  // Check if a node type is active
  const isNodeActive = (nodeType: any, attrs?: any) => {
    const { $from, to, node } = selection;
    if (node) {
      return node.hasMarkup(nodeType, attrs);
    }
    return to <= $from.end() && $from.parent.hasMarkup(nodeType, attrs);
  };

  // Toggle between node types (for headings vs paragraph)
  const toggleBlockType = (nodeType: any, attrs?: any) => {
    return (state: any, dispatch: any) => {
      const isActive = isNodeActive(nodeType, attrs);
      
      if (isActive) {
        // If active, change back to paragraph
        return setBlockType(schema.nodes.paragraph)(state, dispatch);
      } else {
        // If not active, change to the target node type
        return setBlockType(nodeType, attrs)(state, dispatch);
      }
    };
  };

  // Toggle list function
  const toggleList = (listType: any) => {
    return (state: any, dispatch: any) => {
      const { $from, $to } = state.selection;
      const range = $from.blockRange($to);
      
      if (!range) return false;
      
      // Check if we're already in this type of list
      if (range.parent.type === listType) {
        // If we're in the list, lift out of it
        return liftListItem(schema.nodes.list_item)(state, dispatch);
      } else {
        // If we're not in the list, wrap in it
        return wrapInList(listType)(state, dispatch);
      }
    };
  };

  // Execute command
  const runCommand = (command: any) => {
    return () => {
      if (command(editorState, editorView.dispatch)) {
        editorView.focus();
      }
    };
  };

  // Insert @-reference
  const insertReference = () => {
    const { tr } = editorState;
    const referenceNode = schema.nodes.reference.create({
      reference: "character/example",
      type: "character"
    });
    
    const transaction = tr.replaceSelectionWith(referenceNode);
    editorView.dispatch(transaction);
    editorView.focus();
  };

  return (
    <div className={cn(
      "flex items-center gap-1 p-2 border-b bg-background",
      className
    )}>
      {/* Text formatting */}
      <div className="flex items-center gap-1">
        <ToolbarButton
          onClick={runCommand(toggleMark(schema.marks.strong))}
          isActive={isMarkActive(schema.marks.strong)}
          title="Bold (Ctrl+B)"
        >
          <Bold className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(toggleMark(schema.marks.em))}
          isActive={isMarkActive(schema.marks.em)}
          title="Italic (Ctrl+I)"
        >
          <Italic className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(toggleMark(schema.marks.code))}
          isActive={isMarkActive(schema.marks.code)}
          title="Code"
        >
          <Code className="h-4 w-4" />
        </ToolbarButton>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Headings */}
      <div className="flex items-center gap-1">
        <ToolbarButton
          onClick={runCommand(toggleBlockType(schema.nodes.heading, { level: 1 }))}
          isActive={isNodeActive(schema.nodes.heading, { level: 1 })}
          title="Heading 1"
        >
          <Heading1 className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(toggleBlockType(schema.nodes.heading, { level: 2 }))}
          isActive={isNodeActive(schema.nodes.heading, { level: 2 })}
          title="Heading 2"
        >
          <Heading2 className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(toggleBlockType(schema.nodes.heading, { level: 3 }))}
          isActive={isNodeActive(schema.nodes.heading, { level: 3 })}
          title="Heading 3"
        >
          <Heading3 className="h-4 w-4" />
        </ToolbarButton>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Lists and blocks */}
      <div className="flex items-center gap-1">
        <ToolbarButton
          onClick={runCommand(toggleList(schema.nodes.bullet_list))}
          isActive={isNodeActive(schema.nodes.bullet_list)}
          title="Bullet List"
        >
          <List className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(toggleList(schema.nodes.ordered_list))}
          isActive={isNodeActive(schema.nodes.ordered_list)}
          title="Numbered List"
        >
          <ListOrdered className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={runCommand(wrapIn(schema.nodes.blockquote))}
          isActive={isNodeActive(schema.nodes.blockquote)}
          title="Quote"
        >
          <Quote className="h-4 w-4" />
        </ToolbarButton>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Fiction-specific */}
      <div className="flex items-center gap-1">
        <ToolbarButton
          onClick={insertReference}
          title="Insert Reference (@character, @location, etc.)"
        >
          <AtSign className="h-4 w-4" />
        </ToolbarButton>
      </div>
    </div>
  );
}