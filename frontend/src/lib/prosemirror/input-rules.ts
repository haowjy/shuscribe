import { inputRules, wrappingInputRule, textblockTypeInputRule, InputRule } from "prosemirror-inputrules";
import { NodeType, MarkType } from "prosemirror-model";

// Create input rules for markdown shortcuts
export function createMarkdownInputRules(schema: any) {
  const rules: InputRule[] = [];

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

  // Bold rule: **text**
  rules.push(
    new InputRule(
      /\*\*([^*]+)\*\*$/,
      (state, match, start, end) => {
        const { tr } = state;
        if (match[1]) {
          tr.replaceWith(start, end, schema.text(match[1], [schema.marks.strong.create()]));
          return tr;
        }
        return null;
      }
    )
  );

  // Italic rule: *text*
  rules.push(
    new InputRule(
      /(?<!\*)\*([^*]+)\*$/,
      (state, match, start, end) => {
        const { tr } = state;
        if (match[1]) {
          tr.replaceWith(start, end, schema.text(match[1], [schema.marks.em.create()]));
          return tr;
        }
        return null;
      }
    )
  );

  // Code rule: `text`
  rules.push(
    new InputRule(
      /`([^`]+)`$/,
      (state, match, start, end) => {
        const { tr } = state;
        if (match[1]) {
          tr.replaceWith(start, end, schema.text(match[1], [schema.marks.code.create()]));
          return tr;
        }
        return null;
      }
    )
  );

  return inputRules({ rules });
}