import { inputRules, wrappingInputRule, textblockTypeInputRule, InputRule, smartQuotes, emDash, ellipsis } from "prosemirror-inputrules";
import { NodeType, MarkType } from "prosemirror-model";

/**
 * Helper that turns a `RegExp` + `MarkType` into an `InputRule`
 * with proper bounds checking
 */
function markInputRule(regexp: RegExp, markType: any) {
  return new InputRule(regexp, (state, match, start, end) => {
    const $start = state.doc.resolve(start);
    const $end = state.doc.resolve(end);

    if (!$start.parent.canReplaceWith($start.index(), $end.index(), state.schema.text(match[1]))) {
      return null;
    }

    const tr = state.tr;
    const matchStart = start + match.index;
    const matchEnd = matchStart + match[0].length;

    if (match[1]) {
      const textStart = matchStart + match[0].indexOf(match[1]);
      const textEnd = textStart + match[1].length;

      // Delete the markdown syntax
      tr.delete(matchStart, matchEnd);

      // Insert the text with the mark
      const node = state.schema.text(match[1], [markType.create()]);
      tr.insert(matchStart, node);
    }

    return tr;
  });
}

// Create input rules for markdown shortcuts
export function createMarkdownInputRules(schema: any) {
  const rules: InputRule[] = smartQuotes.concat(ellipsis, emDash);

  // Heading rules
  for (let level = 1; level <= 6; level++) {
    rules.push(
      textblockTypeInputRule(
        new RegExp(`^(#{${level}})\\s$`),
        schema.nodes.heading,
        { level }
      )
    );
  }

  // Blockquote rule
  rules.push(
    wrappingInputRule(/^\s*>\s$/, schema.nodes.blockquote)
  );

  // Code block rule
  rules.push(
    textblockTypeInputRule(/^```$/, schema.nodes.code_block)
  );

  // Bullet list rule
  rules.push(
    wrappingInputRule(/^\s*([-+*])\s$/, schema.nodes.bullet_list)
  );

  // Ordered list rule
  rules.push(
    wrappingInputRule(
      /^(\d+)\.\s$/,
      schema.nodes.ordered_list,
      (match) => ({ order: +match[1] }),
      (match, node) => node.childCount + node.attrs.order == +match[1]
    )
  );

  // Enhanced markdown input rules with smart conflict resolution

  // **bold** - improved pattern
  if (schema.marks.strong) {
    rules.push(markInputRule(/\*\*([^*\s][^*]*[^*\s]|\S)\*\*$/, schema.marks.strong));
  }

  // *italic* - but not at start of line (to avoid conflict with bullet lists)
  if (schema.marks.em) {
    rules.push(markInputRule(/(?:^|[^*\s])\*([^*\s][^*]*[^*\s]|\S)\*$/, schema.marks.em));
  }

  // `code` - inline code (single backticks)
  if (schema.marks.code) {
    rules.push(markInputRule(/`([^`\s][^`]*[^`\s]|[^`\s])`$/, schema.marks.code));
  }

  return inputRules({ rules });
}