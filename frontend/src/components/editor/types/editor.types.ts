import { Editor } from "@tiptap/react";
import { LucideIcon } from "lucide-react";

// Rail mode types for contextual toolbar behavior
export type RailMode = 'workspace' | 'component-gallery' | 'devtools' | 'settings' | 'series' | 'articles' | 'projects';

// Supported editor commands for toolbar/actions
export type EditorCommand =
  | "undo"
  | "redo"
  | "toggleBold"
  | "toggleItalic"
  | "toggleUnderline"
  | "toggleStrike"
  | "toggleCode"
  | "toggleHighlight"
  | "toggleSubscript"
  | "toggleSuperscript"
  | "setParagraph"
  | "toggleHeading"
  | "setTextAlign"
  | "toggleBulletList"
  | "toggleOrderedList"
  | "toggleTaskList"
  | "toggleBlockquote"
  | "toggleCodeBlock"
  | "setHorizontalRule"
  | "insertTable"
  | "addColumnBefore"
  | "addColumnAfter"
  | "addRowBefore"
  | "addRowAfter"
  | "mergeCells"
  | "splitCell"
  | "deleteColumn"
  | "deleteRow"
  | "deleteTable";

// Toolbar section types
export type ToolbarSection = 'history' | 'textStyle' | 'formatting' | 'lists' | 'alignment' | 'blocks' | 'insert' | 'table';

// Toolbar configuration interface
export interface ToolbarConfig {
  show?: boolean; // Whether to show toolbar at all (default: true)
  sections?: ToolbarSection[]; // Which sections to include (default: all)
  commands?: EditorCommand[]; // Which specific commands to include (default: all)
}

// Footer configuration interface  
export interface FooterConfig {
  show?: boolean; // Whether to show footer at all (default: true)
  showCharacterCount?: boolean; // Show character count (default: true)
  showWordCount?: boolean; // Show word count (default: true)
  showStats?: boolean; // Show additional stats (default: false)
}

// Extension configuration interface
export interface ExtensionConfig {
  overrides?: {
    starterKit?: Partial<StarterKitConfig>;
    textAlign?: Partial<TextAlignConfig>;
    highlight?: Partial<HighlightConfig>;
    link?: Partial<LinkConfig>;
    image?: Partial<ImageConfig>;
    taskItem?: Partial<TaskItemConfig>;
    table?: Partial<TableConfig>;
  };
  // TODO: Add support for custom extensions array
  // extraExtensions?: Extension[];
}

// Main editor component props
export interface DocumentEditorProps {
  content?: string;
  placeholder?: string;
  onUpdate?: (content: string) => void;
  className?: string;
  toolbar?: ToolbarConfig;
  footer?: FooterConfig;
  extensions?: ExtensionConfig;
  editable?: boolean; // whether editor is editable (default true)
  railMode?: RailMode; // contextual rail mode for toolbar behavior
  // Styling customization props
  border?: boolean | string; // false, true, or custom border classes
  rounded?: boolean | string; // false, true, or custom rounded classes
  container?: string; // custom container classes
  // Height control props
  height?: string; // explicit height (e.g., "400px", "50vh")
  minHeight?: string | number; // minimum height override (e.g., "200px", 200)
  // Paper mode props
  paperMode?: boolean | 'A4' | 'letter' | 'legal'; // enables page-like appearance with predefined or default page size
  autoPagination?: boolean; // enables automatic page breaks when content overflows (requires paperMode)
  // TODO: Add more customization props for lightweight editor variants:
  // - autofocus?: boolean | 'start' | 'end' | number
  // - editorProps?: Record<string, any>
  // - onImageUpload?: (file: File) => Promise<string>
  // - characterLimit?: number
}

// Editor state interface for useEditorState selector
export interface EditorState {
  // Text formatting states
  isBold?: boolean;
  isItalic?: boolean;
  isUnderline?: boolean;
  isStrike?: boolean;
  isCode?: boolean;
  isHighlight?: boolean;
  isSubscript?: boolean;
  isSuperscript?: boolean;

  // Heading states
  isHeading1?: boolean;
  isHeading2?: boolean;
  isHeading3?: boolean;

  // Text alignment states
  isAlignLeft?: boolean;
  isAlignCenter?: boolean;
  isAlignRight?: boolean;
  isAlignJustify?: boolean;

  // List states
  isBulletList?: boolean;
  isOrderedList?: boolean;
  isTaskList?: boolean;

  // Block states
  isBlockquote?: boolean;
  isCodeBlock?: boolean;

  // Command availability
  canUndo?: boolean;
  canRedo?: boolean;
}

// Base button configuration interface
export interface BaseButtonConfig {
  id: string;
  icon: LucideIcon;
  tooltip: string;
  command: EditorCommand;
  shortcutKeys?: string;
}

// Toolbar button configuration interface
export interface ToolbarButtonConfig {
  id: string;
  icon: LucideIcon;
  tooltip: string;
  command: EditorCommand;
  shortcutKeys?: string;
  stateKey?: keyof EditorState;
}

// Text style option interface
export interface TextStyleOption {
  id: string;
  label: string;
  icon: LucideIcon;
  command: EditorCommand;
  level: number | null;
}

// Text alignment option interface
export interface TextAlignmentOption {
  id: string;
  label: string;
  icon: LucideIcon;
  command: EditorCommand;
  value: string;
}

// Special formatting option interface
export interface SpecialFormattingOption {
  id: string;
  label: string;
  icon: LucideIcon;
  command: EditorCommand;
  stateKey: keyof EditorState;
}

// Table option interface
export interface TableOption {
  id: string;
  label: string;
  icon: LucideIcon;
  command: EditorCommand;
  params?: { rows: number; cols: number; withHeaderRow: boolean };
  variant?: "default" | "destructive";
}

// Dynamic format button props
export interface DynamicFormatButtonProps {
  isActive: boolean;
  command: () => void;
  icon: React.ComponentType<{ size?: number }>;
  tooltip: string;
  shortcutKeys?: string;
}

// Toolbar section props
export interface ToolbarSectionProps {
  children: React.ReactNode;
  className?: string;
}

// Dropdown toolbar button props
export interface DropdownToolbarButtonProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
  tooltip?: string;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  align?: "start" | "center" | "end";
  className?: string;
  contentClassName?: string;
  onCloseAutoFocus?: (event: Event) => void;
}

// Text style dropdown props
export interface TextStyleDropdownProps {
  editor: Editor | null;
  editorState: EditorState | null;
  currentTextStyle: CurrentStyleState;
  textStyleOpen: boolean;
  setTextStyleOpen: (open: boolean) => void;
}

// Text alignment dropdown props
export interface TextAlignmentDropdownProps {
  editor: Editor | null;
  editorState: EditorState | null;
  currentTextAlignment: CurrentStyleState;
  textAlignmentOpen: boolean;
  setTextAlignmentOpen: (open: boolean) => void;
}

// Special formatting dropdown props
export interface SpecialFormattingDropdownProps {
  editor: Editor | null;
  editorState: EditorState | null;
  specialFormattingOpen: boolean;
  setSpecialFormattingOpen: (open: boolean) => void;
}

// Table dropdown props
export interface TableDropdownProps {
  editor: Editor | null;
  editorState: EditorState | null;
  tableOpen: boolean;
  setTableOpen: (open: boolean) => void;
}

// Editor toolbar props
export interface EditorToolbarProps {
  editor: Editor | null;
  editorState: EditorState | null;
  toolbarState: UseEditorToolbarStateReturn;
  config?: ToolbarConfig;
  railMode?: RailMode;
}

// Editor footer props
export interface EditorFooterProps {
  editor: Editor | null;
  config?: FooterConfig;
}

// Editor statistics interface
export interface EditorStats {
  characters: number;
  charactersWithoutSpaces: number;
  words: number;
  sentences: number;
  paragraphs: number;
}

// Current style state interface
export interface CurrentStyleState {
  label: string;
  icon: LucideIcon;
}

// Upload configuration interface
export interface UploadConfig {
  allowedMimeTypes: readonly string[];
  maxFileSize: number;
  acceptString: string;
}

// Extension configuration interfaces
export interface StarterKitConfig {
  heading?: {
    levels?: [1, 2, 3] | [1, 2] | [1];
  };
  codeBlock?: {
    HTMLAttributes?: {
      class?: string;
    };
  };
}

export interface TextAlignConfig {
  types?: string[];
}

export interface HighlightConfig {
  multicolor?: boolean;
}

export interface LinkConfig {
  openOnClick?: boolean;
  HTMLAttributes?: {
    class?: string;
  };
}

export interface ImageConfig {
  HTMLAttributes?: {
    class?: string;
  };
}

export interface TaskItemConfig {
  nested?: boolean;
}

export interface TableConfig {
  resizable?: boolean;
}

// Editor configuration interface
export interface EditorConfig {
  starterKit: StarterKitConfig;
  textAlign: TextAlignConfig;
  highlight: HighlightConfig;
  link: LinkConfig;
  image: ImageConfig;
  taskItem: TaskItemConfig;
  table: TableConfig;
}

// Editor hook return interface
export interface UseEditorConfigReturn {
  editor: Editor | null;
  editorState: EditorState | null;
}

// Toolbar state hook return interface
export interface UseEditorToolbarStateReturn {
  textStyleOpen: boolean;
  setTextStyleOpen: (open: boolean) => void;
  textAlignmentOpen: boolean;
  setTextAlignmentOpen: (open: boolean) => void;
  specialFormattingOpen: boolean;
  setSpecialFormattingOpen: (open: boolean) => void;
  tableOpen: boolean;
  setTableOpen: (open: boolean) => void;
  currentTextStyle: CurrentStyleState;
  currentTextAlignment: CurrentStyleState;
}

// Command execution parameters - type-safe mapping of commands to their params
export type CommandParamsMap = {
  // Commands with no parameters
  undo: void;
  redo: void;
  toggleBold: void;
  toggleItalic: void;
  toggleUnderline: void;
  toggleStrike: void;
  toggleCode: void;
  toggleHighlight: void;
  toggleSubscript: void;
  toggleSuperscript: void;
  setParagraph: void;
  toggleBulletList: void;
  toggleOrderedList: void;
  toggleTaskList: void;
  toggleBlockquote: void;
  toggleCodeBlock: void;
  setHorizontalRule: void;
  addColumnBefore: void;
  addColumnAfter: void;
  addRowBefore: void;
  addRowAfter: void;
  mergeCells: void;
  splitCell: void;
  deleteColumn: void;
  deleteRow: void;
  deleteTable: void;

  // Commands with parameters
  toggleHeading: { level: 1 | 2 | 3 };
  setTextAlign: { value: 'left' | 'center' | 'right' | 'justify' };
  insertTable: { rows: number; cols: number; withHeaderRow: boolean };
};

// Legacy interface for backwards compatibility (deprecated)
export interface CommandParams {
  level?: number;
  value?: string;
  rows?: number;
  cols?: number;
  withHeaderRow?: boolean;
}

// File handler callbacks
export interface FileHandlerCallbacks {
  onDrop: (editor: Editor, files: File[]) => void;
  onPaste: (editor: Editor, files: File[]) => void;
}

// Editor theme interface
export interface EditorTheme {
  background: string;
  foreground: string;
  border: string;
  muted: string;
  primary: string;
}

// Keyboard shortcut interface
export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  handler: (editor: Editor) => boolean;
}