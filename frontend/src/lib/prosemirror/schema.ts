import { Schema, NodeSpec } from "prosemirror-model";
import { listItem, orderedList, bulletList } from "prosemirror-schema-list";

// Reference node for @-references in fiction writing
const referenceSpec = {
  attrs: { 
    reference: { default: "" },
    type: { default: "character" } // character, location, item, etc.
  },
  inline: true,
  group: "inline",
  draggable: true,
  parseDOM: [
    {
      tag: "span[data-reference]",
      getAttrs: (dom: Element) => ({
        reference: dom.getAttribute("data-reference") || "",
        type: dom.getAttribute("data-reference-type") || "character"
      })
    }
  ],
  toDOM: (node: any) => [
    "span",
    {
      class: "reference-node bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer px-1 py-0.5 rounded text-sm font-medium",
      "data-reference": node.attrs.reference,
      "data-reference-type": node.attrs.type,
    },
    `@${node.attrs.reference}`
  ]
};

// Basic nodes for writing
const baseNodes = {
  doc: {
    content: "block+"
  },
  
  paragraph: {
    content: "inline*",
    group: "block",
    parseDOM: [{ tag: "p" }],
    toDOM: () => ["p", 0]
  },
  
  heading: {
    attrs: { level: { default: 1 } },
    content: "inline*",
    group: "block",
    defining: true,
    parseDOM: [
      { tag: "h1", attrs: { level: 1 } },
      { tag: "h2", attrs: { level: 2 } },
      { tag: "h3", attrs: { level: 3 } },
      { tag: "h4", attrs: { level: 4 } },
      { tag: "h5", attrs: { level: 5 } },
      { tag: "h6", attrs: { level: 6 } }
    ],
    toDOM: (node: any) => [`h${node.attrs.level}`, 0]
  },
  
  blockquote: {
    content: "block+",
    group: "block",
    defining: true,
    parseDOM: [{ tag: "blockquote" }],
    toDOM: () => ["blockquote", 0]
  },
  
  code_block: {
    content: "text*",
    marks: "",
    group: "block",
    code: true,
    defining: true,
    parseDOM: [{ tag: "pre", preserveWhitespace: "full" }],
    toDOM: () => ["pre", ["code", 0]]
  },
  
  text: {
    group: "inline"
  },
  
  reference: referenceSpec,
  
  hard_break: {
    inline: true,
    group: "inline",
    selectable: false,
    parseDOM: [{ tag: "br" }],
    toDOM: () => ["br"]
  }
};

// Add list support manually
const nodesWithLists = {
  ...baseNodes,
  ordered_list: orderedList,
  bullet_list: bulletList,
  list_item: listItem,
};

// Basic marks for text formatting
const marks = {
  strong: {
    parseDOM: [
      { tag: "strong" },
      { tag: "b", getAttrs: (node: any) => node.style.fontWeight !== "normal" && null },
      { style: "font-weight", getAttrs: (value: any) => /^(bold(er)?|[5-9]\d{2,})$/.test(value) && null }
    ],
    toDOM: () => ["strong", 0]
  },
  
  em: {
    parseDOM: [
      { tag: "i" },
      { tag: "em" },
      { style: "font-style=italic" }
    ],
    toDOM: () => ["em", 0]
  },
  
  code: {
    parseDOM: [{ tag: "code" }],
    toDOM: () => ["code", { class: "bg-muted px-1 py-0.5 rounded text-sm" }, 0]
  }
};

// Create the schema
export const fictionSchema = new Schema({
  nodes: nodesWithLists,
  marks
});

// Helper to create empty document
export function createEmptyDoc() {
  return fictionSchema.nodes.doc.create({}, [
    fictionSchema.nodes.paragraph.create()
  ]);
}

// Helper to create document from content
export function createDocFromContent(content: any) {
  if (!content || typeof content !== 'object') {
    return createEmptyDoc();
  }
  
  try {
    return fictionSchema.nodeFromJSON(content);
  } catch (error) {
    console.error("Error creating document from content:", error);
    return createEmptyDoc();
  }
}