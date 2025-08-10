import { Editor } from "@tiptap/react";
import type { EditorCommand, CommandParamsMap, EditorState } from "../types/editor.types";
import { TEXT_STYLE_OPTIONS, TEXT_ALIGNMENT_OPTIONS } from "./editor-constants";

/**
 * Simple mock upload function - in production, replace with real upload logic
 * For now, creates a local object URL for immediate preview
 */
export const handleImageUpload = async (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.readAsDataURL(file);
  });
};

/**
 * Gets the current text style from the editor state
 */
export const getCurrentTextStyle = (editor: Editor | null) => {
  if (!editor) return TEXT_STYLE_OPTIONS[0]; // Default to Normal Text

  // Check for headings first
  if (editor.isActive("heading", { level: 1 })) {
    return TEXT_STYLE_OPTIONS[1]; // Heading 1
  }
  if (editor.isActive("heading", { level: 2 })) {
    return TEXT_STYLE_OPTIONS[2]; // Heading 2
  }
  if (editor.isActive("heading", { level: 3 })) {
    return TEXT_STYLE_OPTIONS[3]; // Heading 3
  }
  
  return TEXT_STYLE_OPTIONS[0]; // Normal Text
};

/**
 * Gets the current text alignment from the editor state
 */
export const getCurrentTextAlignment = (editor: Editor | null) => {
  if (!editor) return TEXT_ALIGNMENT_OPTIONS[0]; // Default to Align Left

  if (editor.isActive({ textAlign: "center" })) {
    return TEXT_ALIGNMENT_OPTIONS[1]; // Center
  }
  if (editor.isActive({ textAlign: "right" })) {
    return TEXT_ALIGNMENT_OPTIONS[2]; // Align Right
  }
  if (editor.isActive({ textAlign: "justify" })) {
    return TEXT_ALIGNMENT_OPTIONS[3]; // Justify
  }
  
  return TEXT_ALIGNMENT_OPTIONS[0]; // Align Left
};

/**
 * Triggers a file input dialog for image upload
 */
export const triggerImageUpload = (editor: Editor, onUpload: (file: File) => Promise<string>) => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) {
      try {
        const url = await onUpload(file);
        editor.chain().focus().setImage({ src: url }).run();
      } catch (error) {
        console.error("Upload failed:", error);
      }
    }
  };
  input.click();
};

/**
 * Command handler type - allows commands with or without parameters
 */
type CommandHandler<C extends EditorCommand> = CommandParamsMap[C] extends void
  ? (editor: Editor) => boolean
  : (editor: Editor, params: CommandParamsMap[C]) => boolean;

/**
 * Command registry - maps commands to their handler functions
 * Type-safe registry ensuring all commands are handled consistently
 */
const commandHandlers: { [K in EditorCommand]: CommandHandler<K> } = {
  // History commands
  undo: (editor: Editor) => editor.chain().focus().undo().run(),
  redo: (editor: Editor) => editor.chain().focus().redo().run(),

  // Basic formatting commands
  toggleBold: (editor: Editor) => editor.chain().focus().toggleBold().run(),
  toggleItalic: (editor: Editor) => editor.chain().focus().toggleItalic().run(),
  toggleUnderline: (editor: Editor) => editor.chain().focus().toggleUnderline().run(),
  toggleStrike: (editor: Editor) => editor.chain().focus().toggleStrike().run(),
  toggleCode: (editor: Editor) => editor.chain().focus().toggleCode().run(),
  toggleHighlight: (editor: Editor) => editor.chain().focus().toggleHighlight().run(),
  toggleSubscript: (editor: Editor) => editor.chain().focus().toggleSubscript().run(),
  toggleSuperscript: (editor: Editor) => editor.chain().focus().toggleSuperscript().run(),

  // Text style commands
  setParagraph: (editor: Editor) => editor.chain().focus().setParagraph().run(),
  toggleHeading: (editor: Editor, params: CommandParamsMap['toggleHeading']) =>
    editor.chain().focus().toggleHeading({ level: params.level }).run(),

  // Text alignment commands
  setTextAlign: (editor: Editor, params: CommandParamsMap['setTextAlign']) =>
    editor.chain().focus().setTextAlign(params.value).run(),

  // List commands
  toggleBulletList: (editor: Editor) => editor.chain().focus().toggleBulletList().run(),
  toggleOrderedList: (editor: Editor) => editor.chain().focus().toggleOrderedList().run(),
  toggleTaskList: (editor: Editor) => editor.chain().focus().toggleTaskList().run(),

  // Block commands
  toggleBlockquote: (editor: Editor) => editor.chain().focus().toggleBlockquote().run(),
  toggleCodeBlock: (editor: Editor) => editor.chain().focus().toggleCodeBlock().run(),

  // Insert commands
  setHorizontalRule: (editor: Editor) => editor.chain().focus().setHorizontalRule().run(),

  // Table commands
  insertTable: (editor: Editor, params: CommandParamsMap['insertTable']) =>
    editor.chain().focus().insertTable(params).run(),
  addColumnBefore: (editor: Editor) => editor.chain().focus().addColumnBefore().run(),
  addColumnAfter: (editor: Editor) => editor.chain().focus().addColumnAfter().run(),
  addRowBefore: (editor: Editor) => editor.chain().focus().addRowBefore().run(),
  addRowAfter: (editor: Editor) => editor.chain().focus().addRowAfter().run(),
  mergeCells: (editor: Editor) => editor.chain().focus().mergeCells().run(),
  splitCell: (editor: Editor) => editor.chain().focus().splitCell().run(),
  deleteColumn: (editor: Editor) => editor.chain().focus().deleteColumn().run(),
  deleteRow: (editor: Editor) => editor.chain().focus().deleteRow().run(),
  deleteTable: (editor: Editor) => editor.chain().focus().deleteTable().run(),
};

/**
 * Type-safe command executor using command registry pattern
 * Provides O(1) lookup performance and per-command parameter typing
 */
export function executeEditorCommand<C extends EditorCommand>(
  editor: Editor,
  command: C,
  ...args: CommandParamsMap[C] extends void ? [] : [CommandParamsMap[C]]
): boolean {
  const handler = commandHandlers[command];
  
  if (!handler) {
    console.warn(`Unknown command: ${command}`);
    return false;
  }

  // Handle commands with and without parameters
  if (args.length > 0) {
    // Command with parameters - TypeScript can't infer the exact handler type at runtime
    return (handler as (editor: Editor, params: unknown) => boolean)(editor, args[0]);
  } else {
    // Command without parameters
    return (handler as (editor: Editor) => boolean)(editor);
  }
}

/**
 * Checks if a special formatting option should be hidden (when it's active)
 */
export const shouldHideSpecialFormattingOption = (
  optionStateKey: string,
  editorState: EditorState | null
): boolean => {
  switch (optionStateKey) {
    case "isUnderline":
      return editorState?.isUnderline || false;
    case "isStrike":
      return editorState?.isStrike || false;
    case "isCode":
      return editorState?.isCode || false;
    case "isSubscript":
      return editorState?.isSubscript || false;
    case "isSuperscript":
      return editorState?.isSuperscript || false;
    default:
      return false;
  }
};

/**
 * Gets the active state for a formatting option
 */
export const getFormattingActiveState = (
  stateKey: keyof EditorState,
  editorState: EditorState | null
): boolean => {
  return (editorState?.[stateKey] as boolean) || false;
};

/**
 * Creates a reusable dropdown close handler that restores focus to editor
 */
export const createDropdownCloseHandler = (editor: Editor) => {
  return (event: Event) => {
    event.preventDefault();
    editor.chain().focus().run();
  };
};

/**
 * Formats character count for display
 */
export const formatCharacterCount = (count: number): string => {
  if (count < 1000) {
    return `${count} chars`;
  }
  if (count < 1000000) {
    return `${(count / 1000).toFixed(1)}k chars`;
  }
  return `${(count / 1000000).toFixed(1)}M chars`;
};

/**
 * Gets editor statistics
 */
export const getEditorStats = (editor: Editor | null) => {
  if (!editor) {
    return {
      characters: 0,
      charactersWithoutSpaces: 0,
      words: 0,
      sentences: 0,
      paragraphs: 0,
    };
  }

  const { characters, words } = editor.storage.characterCount;
  const text = editor.getText();
  
  return {
    characters: characters(),
    charactersWithoutSpaces: text.replace(/\s/g, '').length,
    words: words(),
    sentences: text.split(/[.!?]+/).filter(s => s.trim().length > 0).length,
    paragraphs: editor.getJSON().content?.filter(node => node.type === 'paragraph').length || 0,
  };
};