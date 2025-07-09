import { Plugin, PluginKey } from "prosemirror-state";
import { Decoration, DecorationSet } from "prosemirror-view";
import { inputRules, InputRule } from "prosemirror-inputrules";

// Plugin key for managing state
const referencePluginKey = new PluginKey("reference-plugin");

// Autocomplete callback interface
export interface AutocompleteCallbacks {
  onTrigger?: (query: string, position: { x: number; y: number }) => void;
  onQueryChange?: (query: string) => void;
  onDismiss?: () => void;
  onSelect?: (reference: string, type: string) => void;
}

// Input rule for creating references when autocomplete is not active
function createReferenceInputRule(schema: any) {
  return new InputRule(
    /@([a-zA-Z0-9-_/]+)\s$/,
    (state, match, start, end) => {
      const referenceText = match[1];
      
      // Determine reference type from the path structure
      let referenceType = "document";
      if (referenceText.includes("character/") || referenceText.startsWith("char/")) {
        referenceType = "character";
      } else if (referenceText.includes("location/") || referenceText.startsWith("loc/")) {
        referenceType = "location";
      } else if (referenceText.includes("chapter/") || referenceText.startsWith("ch/")) {
        referenceType = "chapter";
      } else if (referenceText.includes("scene/")) {
        referenceType = "scene";
      } else if (referenceText.includes("note/")) {
        referenceType = "note";
      }
      
      // Create the reference node
      const referenceNode = schema.nodes.reference.create({
        reference: referenceText,
        type: referenceType
      });
      
      // Replace the text with the reference node and add a space
      const tr = state.tr
        .replaceWith(start, end, referenceNode)
        .insertText(" ");
      
      return tr;
    }
  );
}

// Plugin for handling @-reference autocomplete
export function createReferencePlugin(schema: any, callbacks: AutocompleteCallbacks = {}) {
  let viewInstance: any = null;
  
  return new Plugin({
    key: referencePluginKey,
    
    state: {
      init() {
        return {
          activeReference: null,
          referenceStart: null,
          referenceEnd: null,
          decorations: DecorationSet.empty,
          autocompleteActive: false
        };
      },
      
      apply(tr, value, oldState, newState) {
        // Handle decorations and autocomplete trigger for partial @-references
        const { selection } = newState;
        const { $from } = selection;
        
        // Only trigger in text content, not in other node types
        if (!$from.parent.isTextblock) {
          if (value.autocompleteActive && callbacks.onDismiss) {
            callbacks.onDismiss();
          }
          return {
            activeReference: null,
            referenceStart: null,
            referenceEnd: null,
            decorations: DecorationSet.empty,
            autocompleteActive: false
          };
        }
        
        // Check if we're in the middle of typing a reference
        const textBefore = $from.parent.textContent.slice(0, $from.parentOffset);
        const referenceMatch = textBefore.match(/@([a-zA-Z0-9-_/]*)$/);
        
        if (referenceMatch) {
          const query = referenceMatch[1];
          const from = $from.pos - referenceMatch[0].length;
          const to = $from.pos;
          
          // Create decoration for the active reference
          const decoration = Decoration.inline(from, to, {
            class: "reference-typing bg-blue-50 text-blue-700 px-1 rounded border border-blue-200"
          });
          
          // Handle autocomplete trigger/update
          if (viewInstance && callbacks.onTrigger) {
            try {
              const coords = viewInstance.coordsAtPos(to);
              const popupPosition = {
                x: coords.left,
                y: coords.bottom + 4 // Small offset below cursor
              };
              
              // Trigger autocomplete if query changed or if we just started typing
              if (query !== value.activeReference || !value.autocompleteActive) {
                callbacks.onTrigger(query, popupPosition);
              } else if (callbacks.onQueryChange) {
                callbacks.onQueryChange(query);
              }
            } catch (e) {
              console.warn("Error calculating cursor position for autocomplete:", e);
            }
          }
          
          return {
            activeReference: query,
            referenceStart: from,
            referenceEnd: to,
            decorations: DecorationSet.create(newState.doc, [decoration]),
            autocompleteActive: true
          };
        }
        
        // No active reference - dismiss autocomplete if it was active
        if (value.autocompleteActive && callbacks.onDismiss) {
          callbacks.onDismiss();
        }
        
        return {
          activeReference: null,
          referenceStart: null,
          referenceEnd: null,
          decorations: DecorationSet.empty,
          autocompleteActive: false
        };
      }
    },
    
    view: (view) => {
      viewInstance = view;
      return {
        destroy: () => {
          viewInstance = null;
        }
      };
    },
    
    props: {
      decorations(state) {
        return referencePluginKey.getState(state)?.decorations;
      },
      
      handleKeyDown(view, event) {
        const state = referencePluginKey.getState(view.state);
        
        // Handle autocomplete navigation keys
        if (state?.autocompleteActive) {
          switch (event.key) {
            case "Escape":
              if (callbacks.onDismiss) {
                callbacks.onDismiss();
              }
              return true;
            case "ArrowDown":
            case "ArrowUp":
            case "Enter":
            case "Tab":
              // Let autocomplete component handle these
              return false;
          }
        }
        
        return false;
      }
    }
  });
}

// Create input rules for references (fallback when autocomplete is not used)
export function createReferenceInputRules(schema: any) {
  return inputRules({
    rules: [createReferenceInputRule(schema)]
  });
}

// Helper to get plugin state
export function getReferencePluginState(state: any) {
  return referencePluginKey.getState(state);
}

// Helper to insert reference programmatically
export function insertReference(view: any, reference: string, type: string) {
  const state = referencePluginKey.getState(view.state);
  if (!state?.referenceStart || !state?.referenceEnd) return false;
  
  // Create the reference node
  const referenceNode = view.state.schema.nodes.reference.create({
    reference,
    type
  });
  
  // Replace the @query text with the reference node
  const tr = view.state.tr
    .replaceWith(state.referenceStart, state.referenceEnd, referenceNode)
    .insertText(" ");
  
  view.dispatch(tr);
  view.focus();
  
  return true;
}