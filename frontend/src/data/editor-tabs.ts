export interface EditorTab {
  id: string;
  name: string;
  content: object; // ProseMirror JSON document
  isDirty?: boolean;
  isTemp?: boolean;
  filePath?: string;
  order: number;
}

export const mockTabs: EditorTab[] = [
  {
    id: "1",
    name: "elara.md",
    filePath: "characters/protagonists/elara.md",
    content: {
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": { "level": 1 },
          "content": [{ "type": "text", "text": "Elara Brightflame" }]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Character Profile" }]
        },
        {
          "type": "bullet_list",
          "content": [
            {
              "type": "list_item",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Age" },
                    { "type": "text", "text": ": 23" }
                  ]
                }
              ]
            },
            {
              "type": "list_item", 
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Magic" },
                    { "type": "text", "text": ": Fire elemental" }
                  ]
                }
              ]
            },
            {
              "type": "list_item",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Current Status" },
                    { "type": "text", "text": ": Living in exile in " },
                    { "type": "reference", "attrs": { "reference": "locations/capital-city", "type": "location" } }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Physical Description" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Elara stands tall with auburn hair that seems to " },
            { "type": "text", "marks": [{ "type": "em" }], "text": "shimmer" },
            { "type": "text", "text": " with an inner warmth. Her green eyes often betray the " },
            { "type": "text", "marks": [{ "type": "strong" }], "text": "inner turmoil" },
            { "type": "text", "text": " she carries from her past." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Relationships" }]
        },
        {
          "type": "bullet_list",
          "content": [
            {
              "type": "list_item",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "reference", "attrs": { "reference": "characters/protagonists/marcus", "type": "character" } },
                    { "type": "text", "text": ": Her mentor and guide" }
                  ]
                }
              ]
            },
            {
              "type": "list_item",
              "content": [
                {
                  "type": "paragraph", 
                  "content": [
                    { "type": "reference", "attrs": { "reference": "locations/capital-city", "type": "location" } },
                    { "type": "text", "text": ": Where she currently lives in exile" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    isDirty: false,
    order: 0,
  },
  {
    id: "2",
    name: "chapter-01.md",
    filePath: "chapters/chapter-01.md",
    content: {
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": { "level": 1 },
          "content": [{ "type": "text", "text": "Chapter 1: Awakening" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "The morning mist clung to the cobblestones of " },
            { "type": "reference", "attrs": { "reference": "locations/capital-city", "type": "location" } },
            { "type": "text", "text": " as " },
            { "type": "reference", "attrs": { "reference": "characters/protagonists/elara", "type": "character" } },
            { "type": "text", "text": " made her way through the narrow alleys." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Her fingers trembled as she felt the familiar warmth building in her chest. The " },
            { "type": "text", "marks": [{ "type": "strong" }], "text": "fire magic" },
            { "type": "text", "text": " that had once consumed her childhood home was stirring again." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "The Incident" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "marks": [{ "type": "em" }], "text": "Three years ago..." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "The memory came unbidden, as it always did when her powers stirred. The flames dancing in her palms during the family dinner. Her brother's laugh as he asked her to show him the trick again." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "The " },
            { "type": "text", "marks": [{ "type": "em" }], "text": "screaming" },
            { "type": "text", "text": "." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Present Day" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "The tavern door creaked open, and " },
            { "type": "reference", "attrs": { "reference": "characters/protagonists/marcus", "type": "character" } },
            { "type": "text", "text": " looked up from behind the bar." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "\"Another nightmare?\" he asked quietly." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "\"Something like that,\" Elara replied. \"But this time, I think it was real.\"" }
          ]
        }
      ]
    },
    isDirty: false,
    order: 1,
  },
];

export function getTabById(id: string): EditorTab | undefined {
  return mockTabs.find(tab => tab.id === id);
}