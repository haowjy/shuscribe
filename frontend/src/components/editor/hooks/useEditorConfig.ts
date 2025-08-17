import { useEditor, useEditorState } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import CharacterCount from "@tiptap/extension-character-count";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import Highlight from "@tiptap/extension-highlight";
import Subscript from "@tiptap/extension-subscript";
import Superscript from "@tiptap/extension-superscript";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import TaskList from "@tiptap/extension-task-list";
import TaskItem from "@tiptap/extension-task-item";
import { TableKit } from "@tiptap/extension-table";
import FileHandler from "@tiptap/extension-file-handler";
import { TextStyle } from "@tiptap/extension-text-style";
// Removed custom font size / line height controls per UX decision

import { EDITOR_DEFAULTS, EXTENSION_CONFIGS, EDITOR_PROPS, IMAGE_UPLOAD_CONFIG } from "../utils/editor-constants";
import { handleImageUpload } from "../utils/editor-helpers";
import type { UseEditorConfigReturn, EditorState, ExtensionConfig } from "../types/editor.types";


interface UseEditorConfigOptions {
  content?: string;
  placeholder?: string;
  onUpdate?: (content: string) => void;
  extensions?: ExtensionConfig;
  paperMode?: boolean | 'A4' | 'letter' | 'legal';
}

export const useEditorConfig = ({
  content = EDITOR_DEFAULTS.content,
  placeholder = EDITOR_DEFAULTS.placeholder,
  onUpdate,
  extensions = {},
  paperMode = false,
}: UseEditorConfigOptions = {}): UseEditorConfigReturn => {
  // Merge extension configurations with overrides
  const mergedConfigs = {
    starterKit: { ...EXTENSION_CONFIGS.starterKit, ...extensions.overrides?.starterKit },
    textAlign: { ...EXTENSION_CONFIGS.textAlign, ...extensions.overrides?.textAlign },
    highlight: { ...EXTENSION_CONFIGS.highlight, ...extensions.overrides?.highlight },
    link: { ...EXTENSION_CONFIGS.link, ...extensions.overrides?.link },
    image: { ...EXTENSION_CONFIGS.image, ...extensions.overrides?.image },
    taskItem: { ...EXTENSION_CONFIGS.taskItem, ...extensions.overrides?.taskItem },
    table: { ...EXTENSION_CONFIGS.table, ...extensions.overrides?.table },
  };


  // Build extensions array
  const editorExtensions = [
      StarterKit.configure(mergedConfigs.starterKit),
      Placeholder.configure({
        placeholder,
      }),
      CharacterCount,
      Underline,
      TextStyle,
      TextAlign.configure(mergedConfigs.textAlign),
      Highlight.configure(mergedConfigs.highlight),
      Subscript,
      Superscript,
      Link.configure(mergedConfigs.link),
      Image.configure(mergedConfigs.image),
      TaskList,
      TaskItem.configure(mergedConfigs.taskItem),
      TableKit.configure({
        table: mergedConfigs.table,
      }),
      FileHandler.configure({
        allowedMimeTypes: IMAGE_UPLOAD_CONFIG.allowedMimeTypes,
        onDrop: (editor, files) => {
          files.forEach(async (file) => {
            if (file.type.startsWith("image/")) {
              try {
                const url = await handleImageUpload(file);
                editor.chain().focus().setImage({ src: url, alt: "" }).run();
              } catch (error) {
                console.error("Upload failed:", error);
              }
            }
          });
        },
        onPaste: (editor, files) => {
          files.forEach(async (file) => {
            if (file.type.startsWith("image/")) {
              try {
                const url = await handleImageUpload(file);
                editor.chain().focus().setImage({ src: url, alt: "" }).run();
              } catch (error) {
                console.error("Upload failed:", error);
              }
            }
          });
        },
      }),
      // TODO: Add support for extra extensions
      // ...(extensions.extraExtensions || []),
    ];


  const editor = useEditor({
    extensions: editorExtensions,
    content,
    immediatelyRender: false,
    onUpdate: onUpdate
      ? ({ editor }) => {
          const html = editor.getHTML();
          onUpdate(html);
        }
      : undefined,
    editorProps: EDITOR_PROPS,
  });

  const editorState = useEditorState({
    editor,
    selector: ({ editor }): EditorState => {
      if (!editor) return {};

      return {
        // Text formatting states
        isBold: editor.isActive("bold"),
        isItalic: editor.isActive("italic"),
        isUnderline: editor.isActive("underline"),
        isStrike: editor.isActive("strike"),
        isCode: editor.isActive("code"),
        isHighlight: editor.isActive("highlight"),
        isSubscript: editor.isActive("subscript"),
        isSuperscript: editor.isActive("superscript"),

        // Heading states
        isHeading1: editor.isActive("heading", { level: 1 }),
        isHeading2: editor.isActive("heading", { level: 2 }),
        isHeading3: editor.isActive("heading", { level: 3 }),

        // Text alignment states
        isAlignLeft:
          !editor.isActive({ textAlign: "center" }) &&
          !editor.isActive({ textAlign: "right" }) &&
          !editor.isActive({ textAlign: "justify" }),
        isAlignCenter: editor.isActive({ textAlign: "center" }),
        isAlignRight: editor.isActive({ textAlign: "right" }),
        isAlignJustify: editor.isActive({ textAlign: "justify" }),

        // List states
        isBulletList: editor.isActive("bulletList"),
        isOrderedList: editor.isActive("orderedList"),
        isTaskList: editor.isActive("taskList"),

        // Block states
        isBlockquote: editor.isActive("blockquote"),
        isCodeBlock: editor.isActive("codeBlock"),

        // Command availability
        canUndo: editor.can().undo(),
        canRedo: editor.can().redo(),
      };
    },
  });

  return {
    editor,
    editorState,
  };
};