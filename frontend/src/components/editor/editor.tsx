"use client";

import React, { useEffect, useRef, useCallback, useState } from "react";
import { EditorView } from "prosemirror-view";
import { EditorState } from "prosemirror-state";
import { keymap } from "prosemirror-keymap";
import { history, undo, redo } from "prosemirror-history";
import { baseKeymap, exitCode, splitBlockKeepMarks, chainCommands, newlineInCode, createParagraphNear, liftEmptyBlock, toggleMark } from "prosemirror-commands";
import { wrapInList, liftListItem, sinkListItem, splitListItem } from "prosemirror-schema-list";
import { inputRules, wrappingInputRule, textblockTypeInputRule, smartQuotes, emDash, ellipsis, InputRule } from "prosemirror-inputrules";
import codemark from "prosemirror-codemark";
import "prosemirror-codemark/dist/codemark.css";
import { dropCursor } from "prosemirror-dropcursor";
import { gapCursor } from "prosemirror-gapcursor";
import { DOMParser, DOMSerializer } from "prosemirror-model";

import { fictionSchema, createEmptyDoc, createDocFromContent } from "@/lib/prosemirror/schema";
import { createReferencePlugin, createReferenceInputRules, insertReference, AutocompleteCallbacks } from "@/lib/prosemirror/reference-plugin";
import { createMarkdownInputRules } from "@/lib/prosemirror/input-rules";
import { EditorToolbar } from "./editor-toolbar";
import { ReferenceAutocomplete, ReferenceItem, ReferenceAutocompleteHandle } from "./reference-autocomplete";
import { useProjectData } from "@/lib/query/hooks";
import { useSearchIndex } from "@/lib/search/index";
import { convertSearchToReferenceItems, createReferenceString, getReferenceType } from "@/lib/search/reference-utils";
import { cn } from "@/lib/utils";


// Custom command to handle backspace in lists
function backspaceCommand(state: EditorState, dispatch?: any) {
  const { $cursor } = state.selection as any;
  if (!$cursor || $cursor.pos !== $cursor.start()) return false;

  const $cut = $cursor;

  // Check if we're in a list item
  for (let d = $cut.depth; d >= 0; d--) {
    const node = $cut.node(d);
    if (node.type === state.schema.nodes.list_item) {
      // If we're at the start of a list item and it's empty, lift it
      if ($cut.index(d) === 0) {
        if (node.content.size === 0 || (node.firstChild && node.firstChild.content.size === 0)) {
          return liftListItem(state.schema.nodes.list_item)(state, dispatch);
        }
      }
      break;
    }
  }

  return false;
}

// Custom command to handle enter in lists
function enterCommand(state: EditorState, dispatch?: any) {
  const { $from, $to } = state.selection;

  // Check if we're in a list item
  for (let d = $from.depth; d >= 0; d--) {
    const node = $from.node(d);
    if (node.type === state.schema.nodes.list_item) {
      // If the list item is empty, exit the list
      if (node.content.size === 0 || (node.firstChild && node.firstChild.content.size === 0)) {
        return liftListItem(state.schema.nodes.list_item)(state, dispatch);
      }
      // Otherwise, split the list item
      return splitListItem(state.schema.nodes.list_item)(state, dispatch);
    }
  }

  return false;
}

interface EditorProps {
  content?: object; // ProseMirror JSON content
  onChange?: (content: object) => void;
  onUpdate?: (content: object) => void;
  placeholder?: string;
  className?: string;
  editable?: boolean;
  projectId?: string; // For search index
}

export function Editor({
  content,
  onChange,
  onUpdate,
  placeholder = "Start writing...",
  className,
  editable = true,
  projectId,
}: EditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [editorState, setEditorState] = useState<EditorState | null>(null);
  const [isFocused, setIsFocused] = useState(false);
  const updateTimeoutRef = useRef<NodeJS.Timeout>();
  
  // Autocomplete state
  const [autocompleteQuery, setAutocompleteQuery] = useState<string>('');
  const [autocompletePosition, setAutocompletePosition] = useState<{ x: number; y: number } | null>(null);
  const [autocompleteItems, setAutocompleteItems] = useState<ReferenceItem[]>([]);
  const [isAutocompleteVisible, setIsAutocompleteVisible] = useState(false);
  const autocompleteRef = useRef<ReferenceAutocompleteHandle>(null);
  
  // Search index for autocomplete
  const { data: projectData } = useProjectData(projectId || '');
  const { search } = useSearchIndex(projectData);
  
  // Add some fallback mock data for testing
  React.useEffect(() => {
    if (!projectData) {
      console.log('No project data available for autocomplete');
    } else {
      console.log('Project data loaded:', projectData);
    }
  }, [projectData]);
  
  // Mock search function for testing if no project data
  const mockSearch = useCallback((query: string) => {
    const mockItems = [
      { id: '1', title: 'Aria Blackwood', path: 'character/aria-blackwood', type: 'file' as const, tags: ['character', 'protagonist'] },
      { id: '2', title: 'Crystal Tower', path: 'location/crystal-tower', type: 'file' as const, tags: ['location', 'magical'] },
      { id: '3', title: 'The Awakening', path: 'chapter/the-awakening', type: 'file' as const, tags: ['chapter', 'opening'] },
    ];
    return mockItems.filter(item => item.title.toLowerCase().includes(query.toLowerCase()));
  }, []);
  
  const searchFn = search || mockSearch;
  
  // Autocomplete callbacks
  const autocompleteCallbacks: AutocompleteCallbacks = {
    onTrigger: useCallback((query: string, position: { x: number; y: number }) => {
      console.log('Autocomplete triggered:', query, position);
      setAutocompleteQuery(query);
      setAutocompletePosition(position);
      
      // Search for references
      const searchResults = searchFn(query, 8);
      const referenceItems = convertSearchToReferenceItems(searchResults);
      console.log('Search results:', searchResults, 'Reference items:', referenceItems);
      setAutocompleteItems(referenceItems);
      setIsAutocompleteVisible(true);
    }, [searchFn]),
    
    onQueryChange: useCallback((query: string) => {
      console.log('Autocomplete query changed:', query);
      setAutocompleteQuery(query);
      
      // Update search results
      const searchResults = searchFn(query, 8);
      const referenceItems = convertSearchToReferenceItems(searchResults);
      setAutocompleteItems(referenceItems);
    }, [searchFn]),
    
    onDismiss: useCallback(() => {
      console.log('Autocomplete dismissed');
      setIsAutocompleteVisible(false);
      setAutocompleteQuery('');
      setAutocompletePosition(null);
      setAutocompleteItems([]);
    }, []),
  };
  
  // Handle autocomplete selection
  const handleAutocompleteSelect = useCallback((item: ReferenceItem) => {
    if (viewRef.current) {
      const referenceString = createReferenceString(item);
      const referenceType = getReferenceType(referenceString);
      
      // Insert the reference
      const success = insertReference(viewRef.current, referenceString, referenceType);
      if (success) {
        // Dismiss autocomplete
        autocompleteCallbacks.onDismiss?.();
      }
    }
  }, [autocompleteCallbacks]);
  
  // Handle keyboard events for autocomplete
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isAutocompleteVisible || !autocompleteRef.current) return;
      
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          autocompleteRef.current.selectNext();
          break;
        case 'ArrowUp':
          event.preventDefault();
          autocompleteRef.current.selectPrevious();
          break;
        case 'Enter':
        case 'Tab':
          event.preventDefault();
          autocompleteRef.current.selectCurrent();
          break;
        case 'Escape':
          event.preventDefault();
          autocompleteRef.current.close();
          break;
      }
    };
    
    if (isAutocompleteVisible) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isAutocompleteVisible]);

  // Initialize editor
  useEffect(() => {
    if (!editorRef.current) return;

    // Create initial document
    const doc = content ? createDocFromContent(content) : createEmptyDoc();

    // Create editor state
    const state = EditorState.create({
      doc,
      plugins: [
        // Original markdown input rules (includes code blocks, basic headings, lists)
        createMarkdownInputRules(fictionSchema),
        
        // Input rules for references
        createReferenceInputRules(fictionSchema),
        
        // Reference plugin for highlighting and autocomplete
        createReferencePlugin(fictionSchema, autocompleteCallbacks),
        
        // Professional inline code handling with prosemirror-codemark
        ...codemark({ markType: fictionSchema.marks.code }),
        
        // History
        history(),
        
        // Enhanced keymap with comprehensive shortcuts
        keymap({
          // Text formatting
          "Mod-b": toggleMark(fictionSchema.marks.strong),
          "Mod-i": toggleMark(fictionSchema.marks.em),
          "Mod-`": toggleMark(fictionSchema.marks.code),
          
          // History
          "Mod-z": undo,
          "Mod-Shift-z": redo,
          "Mod-y": redo,
          
          // Enhanced Enter with mark persistence and list support
          "Enter": chainCommands(
            enterCommand, // Handle lists first
            chainCommands(newlineInCode, createParagraphNear, liftEmptyBlock, splitBlockKeepMarks)
          ),
          
          // Enhanced Backspace with list support
          "Backspace": chainCommands(backspaceCommand, baseKeymap["Backspace"]),
          
          // List navigation
          "Tab": sinkListItem(fictionSchema.nodes.list_item),
          "Shift-Tab": liftListItem(fictionSchema.nodes.list_item),
          
          // List creation shortcuts
          "Mod-Shift-8": wrapInList(fictionSchema.nodes.bullet_list),
          "Mod-Shift-9": wrapInList(fictionSchema.nodes.ordered_list),
          
          // Code block handling
          "Ctrl-Enter": exitCode,
          "Shift-Enter": (state, dispatch) => {
            // Try exitCode first for code blocks
            if (exitCode(state, dispatch)) {
              return true;
            }
            // Fall back to default behavior
            return false;
          },
          
          // Enhanced arrow key navigation for code blocks
          "ArrowDown": (state, dispatch) => {
            const { selection } = state;
            const { $from } = selection;
            
            // Check if we're in a code block and at the end
            if (selection.empty && $from.parent.type.name === "code_block") {
              // Check if cursor is at the very end of the code block
              const codeBlockNode = $from.parent;
              const isAtEnd = $from.parentOffset === codeBlockNode.content.size;
              
              if (isAtEnd) {
                // Exit the code block
                if (exitCode(state, dispatch)) {
                  return true;
                }
              }
            }
            
            // Fall back to default arrow behavior
            return false;
          },
          
          "ArrowUp": (state, dispatch) => {
            const { selection } = state;
            const { $from } = selection;
            
            // Check if we're in a code block and at the beginning
            if (selection.empty && $from.parent.type.name === "code_block") {
              // Check if cursor is at the very beginning of the code block
              const isAtStart = $from.parentOffset === 0;
              
              if (isAtStart) {
                // Try to move cursor above the code block
                const beforeCodeBlock = $from.before();
                if (beforeCodeBlock > 0) {
                  const $target = state.doc.resolve(beforeCodeBlock);
                  if (dispatch) {
                    dispatch(state.tr.setSelection(state.selection.constructor.near($target) as any));
                  }
                  return true;
                }
              }
            }
            
            // Fall back to default arrow behavior
            return false;
          },
          
          // Keep other base keymap commands
          ...baseKeymap,
        }),
        
        // Cursor plugins
        dropCursor(),
        gapCursor(),
      ],
    });

    // Create editor view
    const view = new EditorView(editorRef.current, {
      state,
      editable: () => editable,
      
      dispatchTransaction: (tr) => {
        const newState = view.state.apply(tr);
        view.updateState(newState);
        setEditorState(newState);

        // Handle content changes
        if (tr.docChanged) {
          const newContent = newState.doc.toJSON();
          
          // Debounce updates
          if (updateTimeoutRef.current) {
            clearTimeout(updateTimeoutRef.current);
          }
          
          updateTimeoutRef.current = setTimeout(() => {
            onChange?.(newContent);
            onUpdate?.(newContent);
          }, 150);
        }
      },
      
      handleDOMEvents: {
        focus: () => {
          setIsFocused(true);
          return false;
        },
        blur: () => {
          setIsFocused(false);
          return false;
        },
      },
      
      attributes: {
        class: cn(
          "prose prose-sm max-w-none focus:outline-none",
          "text-foreground text-sm leading-relaxed",
          "[&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-4 [&_h1]:mt-6",
          "[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mb-3 [&_h2]:mt-5", 
          "[&_h3]:text-lg [&_h3]:font-medium [&_h3]:mb-2 [&_h3]:mt-4",
          "[&_p]:mb-4 [&_p]:leading-relaxed",
          "[&_strong]:font-semibold [&_em]:italic",
          "[&_ul]:mb-4 [&_ul]:ml-6 [&_ul]:list-disc",
          "[&_ol]:mb-4 [&_ol]:ml-6 [&_ol]:list-decimal",
          "[&_li]:mb-1",
          "[&_blockquote]:border-l-4 [&_blockquote]:border-muted-foreground [&_blockquote]:pl-4 [&_blockquote]:text-muted-foreground [&_blockquote]:italic",
          className
        ),
      },
    });

    viewRef.current = view;
    setEditorState(state);

    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
      view.destroy();
    };
  }, []); // Only run once on mount

  // Update content when prop changes
  useEffect(() => {
    if (viewRef.current && !isFocused && content) {
      const currentContent = viewRef.current.state.doc.toJSON();
      
      // Simple comparison - in production you might want a deeper comparison
      if (JSON.stringify(currentContent) !== JSON.stringify(content)) {
        const newDoc = createDocFromContent(content);
        const newState = EditorState.create({
          doc: newDoc,
          plugins: viewRef.current.state.plugins,
        });
        
        viewRef.current.updateState(newState);
        setEditorState(newState);
      }
    }
  }, [content, isFocused]);

  // Convert ProseMirror content to markdown for export
  const exportAsMarkdown = useCallback(() => {
    if (!viewRef.current) return "";
    
    const { doc } = viewRef.current.state;
    const serializer = DOMSerializer.fromSchema(fictionSchema);
    const dom = serializer.serializeFragment(doc.content);
    
    const tempDiv = document.createElement("div");
    tempDiv.appendChild(dom);
    
    // Convert to markdown
    let markdown = tempDiv.innerHTML
      .replace(/<h1>(.*?)<\/h1>/g, "# $1\n")
      .replace(/<h2>(.*?)<\/h2>/g, "## $1\n")
      .replace(/<h3>(.*?)<\/h3>/g, "### $1\n")
      .replace(/<strong>(.*?)<\/strong>/g, "**$1**")
      .replace(/<em>(.*?)<\/em>/g, "*$1*")
      .replace(/<code[^>]*>(.*?)<\/code>/g, "`$1`")
      .replace(/<p>(.*?)<\/p>/g, "$1\n\n")
      .replace(/<span[^>]*data-reference="([^"]*)"[^>]*>@[^<]*<\/span>/g, "@$1")
      .replace(/<br\s*\/?>/g, "\n")
      .replace(/&nbsp;/g, " ")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&")
      .trim();
    
    return markdown;
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <EditorToolbar 
        editorView={viewRef.current}
        editorState={editorState}
      />
      
      {/* Editor */}
      <div className="flex-1 relative overflow-auto">
        <div
          ref={editorRef}
          className="w-full h-full min-h-[200px] p-4 focus-within:outline-none"
        />
        
        {/* Placeholder */}
        {!isFocused && (!content || (content.content && content.content.length === 1 && !content.content[0].content)) && (
          <div className="absolute top-4 left-4 text-muted-foreground pointer-events-none">
            {placeholder}
          </div>
        )}
        
        {/* Autocomplete */}
        {isAutocompleteVisible && autocompletePosition && (
          <ReferenceAutocomplete
            ref={autocompleteRef}
            items={autocompleteItems}
            onSelect={handleAutocompleteSelect}
            onClose={autocompleteCallbacks.onDismiss!}
            position={autocompletePosition}
            query={autocompleteQuery}
            className="z-50"
          />
        )}
      </div>
    </div>
  );
}

export default Editor;