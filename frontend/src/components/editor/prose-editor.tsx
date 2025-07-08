"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { EditorView } from "prosemirror-view";
import { EditorState, Transaction } from "prosemirror-state";
import { Schema, DOMParser, DOMSerializer } from "prosemirror-model";
import { schema } from "prosemirror-schema-basic";
import { addListNodes } from "prosemirror-schema-list";
import { keymap } from "prosemirror-keymap";
import { history } from "prosemirror-history";
import { baseKeymap } from "prosemirror-commands";
import { dropCursor } from "prosemirror-dropcursor";
import { gapCursor } from "prosemirror-gapcursor";
import { inputRules, wrappingInputRule, textblockTypeInputRule } from "prosemirror-inputrules";
import { cn } from "@/lib/utils";

// Create schema with list support
const mySchema = new Schema({
  nodes: addListNodes(schema.spec.nodes, "paragraph block*", "block"),
  marks: schema.spec.marks,
});

// Input rules for markdown-like syntax
const blockquoteRule = wrappingInputRule(/^\s*>\s$/, mySchema.nodes.blockquote);
const orderedListRule = wrappingInputRule(
  /^(\d+)\.\s$/,
  mySchema.nodes.ordered_list,
  (match) => ({ order: +match[1] }),
  (match, node) => node.childCount + node.attrs.order == +match[1]
);
const bulletListRule = wrappingInputRule(/^\s*([-+*])\s$/, mySchema.nodes.bullet_list);
const codeBlockRule = textblockTypeInputRule(/^```$/, mySchema.nodes.code_block);
const headingRule = textblockTypeInputRule(
  /^(#{1,6})\s$/,
  mySchema.nodes.heading,
  (match) => ({ level: match[1].length })
);

// Custom @-reference mark
const referenceMarkSpec = {
  attrs: { href: { default: null } },
  inclusive: false,
  parseDOM: [
    {
      tag: "span[data-reference]",
      getAttrs: (dom: Element) => ({ href: dom.getAttribute("data-reference") }),
    },
  ],
  toDOM: (mark: { attrs: { href: string } }) => [
    "span",
    {
      class: "reference-mark bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer px-1 py-0.5 rounded text-sm font-medium",
      "data-reference": mark.attrs.href,
    },
  ],
};

// Extend schema with reference mark
const extendedSchema = new Schema({
  nodes: mySchema.spec.nodes,
  marks: mySchema.spec.marks.addToEnd("reference", referenceMarkSpec),
});

interface ProseEditorProps {
  content: string;
  onChange: (content: string) => void;
  onUpdate?: (content: string) => void;
  placeholder?: string;
  className?: string;
  editable?: boolean;
}

export function ProseEditor({
  content,
  onChange,
  onUpdate,
  placeholder = "Start writing...",
  className,
  editable = true,
}: ProseEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [isFocused, setIsFocused] = useState(false);
  const updateTimeoutRef = useRef<NodeJS.Timeout>();

  // Convert content to ProseMirror document
  const contentToDoc = useCallback((markdownContent: string) => {
    try {
      // First, handle @-references
      const htmlContent = markdownContent.replace(
        /@([a-zA-Z0-9-_/]+)/g,
        '<span data-reference="$1" class="reference-mark">@$1</span>'
      );
      
      // Convert markdown to HTML with proper paragraph handling
      const lines = htmlContent.split('\n');
      const htmlLines: string[] = [];
      let inList = false;
      let inBlockquote = false;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        
        // Empty line - close lists/blockquotes, add paragraph break
        if (trimmed === '') {
          if (inList) {
            htmlLines.push('</ul>');
            inList = false;
          }
          if (inBlockquote) {
            htmlLines.push('</blockquote>');
            inBlockquote = false;
          }
          htmlLines.push('<br>');
          continue;
        }
        
        // Headers
        if (trimmed.startsWith('### ')) {
          htmlLines.push(`<h3>${trimmed.slice(4)}</h3>`);
        } else if (trimmed.startsWith('## ')) {
          htmlLines.push(`<h2>${trimmed.slice(3)}</h2>`);
        } else if (trimmed.startsWith('# ')) {
          htmlLines.push(`<h1>${trimmed.slice(2)}</h1>`);
        }
        // Blockquotes
        else if (trimmed.startsWith('> ')) {
          if (!inBlockquote) {
            htmlLines.push('<blockquote>');
            inBlockquote = true;
          }
          htmlLines.push(`<p>${trimmed.slice(2)}</p>`);
        }
        // List items
        else if (trimmed.startsWith('- ')) {
          if (!inList) {
            htmlLines.push('<ul>');
            inList = true;
          }
          htmlLines.push(`<li>${trimmed.slice(2)}</li>`);
        }
        // Regular paragraphs
        else {
          if (inList) {
            htmlLines.push('</ul>');
            inList = false;
          }
          if (inBlockquote) {
            htmlLines.push('</blockquote>');
            inBlockquote = false;
          }
          htmlLines.push(`<p>${trimmed}</p>`);
        }
      }
      
      // Close any remaining open tags
      if (inList) htmlLines.push('</ul>');
      if (inBlockquote) htmlLines.push('</blockquote>');
      
      // Join and apply inline formatting
      const htmlFormatted = htmlLines.join('\n')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');

      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = htmlFormatted;
      
      return DOMParser.fromSchema(extendedSchema).parse(tempDiv);
    } catch (error) {
      console.error("Error parsing content:", error);
      // Fallback to plain text
      const tempDiv = document.createElement("div");
      tempDiv.textContent = markdownContent;
      return DOMParser.fromSchema(extendedSchema).parse(tempDiv);
    }
  }, []);

  // Convert ProseMirror document to content
  const docToContent = useCallback((doc: { content: unknown }) => {
    try {
      const serializer = DOMSerializer.fromSchema(extendedSchema);
      const dom = serializer.serializeFragment(doc.content);
      const tempDiv = document.createElement("div");
      tempDiv.appendChild(dom);
      
      // Convert back to markdown-style format
      let content = tempDiv.innerHTML;
      
      // Convert references back to @-syntax first
      content = content.replace(
        /<span[^>]*data-reference="([^"]*)"[^>]*>@[^<]*<\/span>/g,
        '@$1'
      );
      
      // Convert HTML back to markdown with better formatting
      content = content
        // Headers
        .replace(/<h1>(.*?)<\/h1>/g, '# $1\n')
        .replace(/<h2>(.*?)<\/h2>/g, '## $1\n')
        .replace(/<h3>(.*?)<\/h3>/g, '### $1\n')
        // Blockquotes
        .replace(/<blockquote><p>(.*?)<\/p><\/blockquote>/gs, (match, content) => {
          return content.split('</p><p>').map((line: string) => `> ${line}`).join('\n') + '\n';
        })
        // Lists
        .replace(/<ul><li>(.*?)<\/li><\/ul>/gs, (match, content) => {
          return content.split('</li><li>').map((item: string) => `- ${item}`).join('\n') + '\n';
        })
        // Inline formatting
        .replace(/<strong>(.*?)<\/strong>/g, '**$1**')
        .replace(/<em>(.*?)<\/em>/g, '*$1*')
        .replace(/<code>(.*?)<\/code>/g, '`$1`')
        // Paragraphs and line breaks
        .replace(/<\/p><p>/g, '\n\n')
        .replace(/<p>/g, '')
        .replace(/<\/p>/g, '\n')
        .replace(/<br\s*\/?>/g, '\n')
        // Clean up entities
        .replace(/&nbsp;/g, ' ')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        // Clean up extra newlines
        .replace(/\n{3,}/g, '\n\n')
        .replace(/\n+$/, '');
      
      return content;
    } catch (error) {
      console.error("Error serializing document:", error);
      return "";
    }
  }, []);

  // Handle @-reference input
  const handleReferenceInput = useCallback((view: EditorView, from: number, to: number, text: string) => {
    // Check if we're completing a reference (space after @reference)
    if (text === " ") {
      const { state } = view;
      const $from = state.doc.resolve(from);
      const textBefore = $from.parent.textContent.slice(0, $from.parentOffset);
      const referenceMatch = textBefore.match(/@([a-zA-Z0-9-_/]+)$/);
      
      if (referenceMatch) {
        const referenceText = referenceMatch[0];
        const referenceStart = from - referenceText.length;
        
        // Create reference mark
        const referenceMark = extendedSchema.marks.reference.create({
          href: referenceMatch[1],
        });
        
        // Replace the @reference text with a marked version and add space
        const tr = state.tr
          .replaceWith(
            referenceStart,
            from,
            extendedSchema.text(referenceText, [referenceMark])
          )
          .insertText(" ", from);
        
        view.dispatch(tr);
        return true;
      }
    }
    
    // Don't interfere with other input
    return false;
  }, []);

  // Initialize editor
  useEffect(() => {
    if (!editorRef.current) return;

    const doc = contentToDoc(content);
    
    const state = EditorState.create({
      doc,
      plugins: [
        inputRules({
          rules: [
            blockquoteRule,
            orderedListRule,
            bulletListRule,
            codeBlockRule,
            headingRule,
          ],
        }),
        keymap({
          "Mod-z": () => {
            if (viewRef.current) {
              return history().spec.props.handleKeyDown?.(viewRef.current, new KeyboardEvent("keydown", { key: "z", metaKey: true })) || false;
            }
            return false;
          },
          "Mod-Shift-z": () => {
            if (viewRef.current) {
              return history().spec.props.handleKeyDown?.(viewRef.current, new KeyboardEvent("keydown", { key: "z", metaKey: true, shiftKey: true })) || false;
            }
            return false;
          },
          ...baseKeymap,
        }),
        history(),
        dropCursor(),
        gapCursor(),
      ],
    });

    const view = new EditorView(editorRef.current, {
      state,
      editable: () => editable,
      dispatchTransaction: (tr: Transaction) => {
        const newState = view.state.apply(tr);
        view.updateState(newState);

        if (tr.docChanged) {
          const newContent = docToContent(newState.doc);
          
          // Debounce updates
          if (updateTimeoutRef.current) {
            clearTimeout(updateTimeoutRef.current);
          }
          
          updateTimeoutRef.current = setTimeout(() => {
            onChange(newContent);
            onUpdate?.(newContent);
          }, 150);
        }
      },
      handleTextInput: (view, from, to, text) => {
        return handleReferenceInput(view, from, to, text);
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
          "w-full h-full max-w-none focus:outline-none",
          "text-foreground text-sm leading-relaxed",
          "[&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-4 [&_h1]:mt-6",
          "[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mb-3 [&_h2]:mt-5",
          "[&_h3]:text-lg [&_h3]:font-medium [&_h3]:mb-2 [&_h3]:mt-4",
          "[&_p]:mb-4 [&_p]:leading-relaxed",
          "[&_strong]:font-semibold [&_em]:italic",
          "[&_code]:bg-muted [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm",
          "[&_blockquote]:border-l-4 [&_blockquote]:border-muted-foreground [&_blockquote]:pl-4 [&_blockquote]:text-muted-foreground [&_blockquote]:italic",
          "[&_ul]:mb-4 [&_ul]:ml-6 [&_ul]:list-disc",
          "[&_ol]:mb-4 [&_ol]:ml-6 [&_ol]:list-decimal",
          "[&_li]:mb-1",
          className
        ),
      },
    });

    viewRef.current = view;

    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
      view.destroy();
    };
  }, [content, onChange, onUpdate, editable, contentToDoc, docToContent, handleReferenceInput, className]);

  // Update content when prop changes
  useEffect(() => {
    if (viewRef.current && !isFocused) {
      const currentContent = docToContent(viewRef.current.state.doc);
      if (currentContent !== content) {
        const newDoc = contentToDoc(content);
        const newState = EditorState.create({
          doc: newDoc,
          plugins: viewRef.current.state.plugins,
        });
        viewRef.current.updateState(newState);
      }
    }
  }, [content, contentToDoc, docToContent, isFocused]);

  return (
    <div className="w-full h-full">
      <div
        ref={editorRef}
        className={cn(
          "w-full h-full min-h-[200px] p-4 focus-within:outline-none",
          !editable && "pointer-events-none opacity-60"
        )}
      />
      {!content && !isFocused && (
        <div className="absolute inset-0 p-4 text-muted-foreground pointer-events-none">
          {placeholder}
        </div>
      )}
    </div>
  );
}