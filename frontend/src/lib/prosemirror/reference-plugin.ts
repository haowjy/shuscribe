import { Plugin, PluginKey } from "prosemirror-state";
import { Decoration, DecorationSet } from "prosemirror-view";
import { inputRules, InputRule } from "prosemirror-inputrules";

// Plugin key for managing state
const referencePluginKey = new PluginKey("reference-plugin");

// Input rule for creating references
function createReferenceInputRule(schema: any) {
  return new InputRule(
    /@([a-zA-Z0-9-_/]+)\s$/,
    (state, match, start, end) => {
      const referenceText = match[1];
      
      // Determine reference type from the path
      let referenceType = "character";
      if (referenceText.includes("location")) {
        referenceType = "location";
      } else if (referenceText.includes("item")) {
        referenceType = "item";
      } else if (referenceText.includes("event")) {
        referenceType = "event";
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

// Plugin for highlighting @-references being typed
export function createReferencePlugin(schema: any) {
  return new Plugin({
    key: referencePluginKey,
    
    state: {
      init() {
        return {
          activeReference: null,
          decorations: DecorationSet.empty
        };
      },
      
      apply(tr, value, oldState, newState) {
        // Handle decorations for partial @-references
        const { selection } = newState;
        const { $from } = selection;
        
        // Check if we're in the middle of typing a reference
        const textBefore = $from.parent.textContent.slice(0, $from.parentOffset);
        const referenceMatch = textBefore.match(/@([a-zA-Z0-9-_/]*)$/);
        
        if (referenceMatch && referenceMatch[1].length > 0) {
          // We're typing a reference, create decoration
          const from = $from.pos - referenceMatch[0].length;
          const to = $from.pos;
          
          const decoration = Decoration.inline(from, to, {
            class: "reference-typing bg-blue-50 text-blue-700 px-1 rounded"
          });
          
          return {
            activeReference: referenceMatch[1],
            decorations: DecorationSet.create(newState.doc, [decoration])
          };
        }
        
        return {
          activeReference: null,
          decorations: DecorationSet.empty
        };
      }
    },
    
    props: {
      decorations(state) {
        return this.getState(state)?.decorations;
      },
      
      handleKeyDown(view, event) {
        const state = this.getState(view.state);
        
        // Handle Escape to cancel reference typing
        if (event.key === "Escape" && state?.activeReference) {
          // Could add logic to cancel reference typing
          return false;
        }
        
        return false;
      }
    }
  });
}

// Create input rules for references
export function createReferenceInputRules(schema: any) {
  return inputRules({
    rules: [createReferenceInputRule(schema)]
  });
}