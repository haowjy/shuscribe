import React from "react";
import { Editor } from "@tiptap/react";
import { getCurrentTextStyle, getCurrentTextAlignment } from "../utils/editor-helpers";
import type { UseEditorToolbarStateReturn, EditorState } from "../types/editor.types";

interface UseEditorToolbarStateOptions {
  editor: Editor | null;
  editorState: EditorState | null;
}

export const useEditorToolbarState = ({
  editor,
  editorState,
}: UseEditorToolbarStateOptions): UseEditorToolbarStateReturn => {
  // Dropdown open states
  const [textStyleOpen, setTextStyleOpen] = React.useState(false);
  const [textAlignmentOpen, setTextAlignmentOpen] = React.useState(false);
  const [specialFormattingOpen, setSpecialFormattingOpen] = React.useState(false);
  const [tableOpen, setTableOpen] = React.useState(false);

  // Memoized current styles to prevent unnecessary re-renders
  const currentTextStyle = React.useMemo(() => {
    return getCurrentTextStyle(editor);
  }, [editor, editorState?.isHeading1, editorState?.isHeading2, editorState?.isHeading3]);

  const currentTextAlignment = React.useMemo(() => {
    return getCurrentTextAlignment(editor);
  }, [editor, editorState?.isAlignLeft, editorState?.isAlignCenter, editorState?.isAlignRight, editorState?.isAlignJustify]);

  return {
    textStyleOpen,
    setTextStyleOpen,
    textAlignmentOpen,
    setTextAlignmentOpen,
    specialFormattingOpen,
    setSpecialFormattingOpen,
    tableOpen,
    setTableOpen,
    currentTextStyle,
    currentTextAlignment,
  };
};