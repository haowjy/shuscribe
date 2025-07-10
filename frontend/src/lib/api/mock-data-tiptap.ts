// Mock API data with proper Tiptap JSON format (no custom references)

import { Document, ProjectData, FileItem } from '@/types/project';

// Document storage with clean Tiptap format
export const mockDocuments: Record<string, Document> = {
  'doc-elara-123': {
    id: 'doc-elara-123',
    projectId: 'project-fantasy-novel',
    title: 'Elara Brightflame',
    path: '/characters/protagonists/elara.md',
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
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Age" },
                    { "type": "text", "text": ": 23" }
                  ]
                }
              ]
            },
            {
              "type": "listItem", 
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Magic" },
                    { "type": "text", "text": ": Fire elemental" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Current Status" },
                    { "type": "text", "text": ": Living in exile in Capital City" }
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
            { "type": "text", "marks": [{ "type": "italic" }], "text": "shimmer" },
            { "type": "text", "text": " with an inner warmth. Her green eyes often betray the " },
            { "type": "text", "marks": [{ "type": "bold" }], "text": "inner turmoil" },
            { "type": "text", "text": " she carries from her past." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Relationships" }]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Marcus Stonehart" },
                    { "type": "text", "text": ": Her mentor and guide" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph", 
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Capital City" },
                    { "type": "text", "text": ": Where she currently lives in exile" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    tags: ['fire-magic', 'trauma', 'protagonist'],
    wordCount: 127,
    createdAt: '2024-01-15T08:30:00Z',
    updatedAt: '2024-01-16T14:22:00Z'
  },

  'doc-marcus-456': {
    id: 'doc-marcus-456',
    projectId: 'project-fantasy-novel',
    title: 'Marcus Stonehart',
    path: '/characters/protagonists/marcus.md',
    content: {
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": { "level": 1 },
          "content": [{ "type": "text", "text": "Marcus Stonehart" }]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Character Profile" }]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Age" },
                    { "type": "text", "text": ": 45" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Magic" },
                    { "type": "text", "text": ": Earth elemental" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Role" },
                    { "type": "text", "text": ": Mentor to Elara Brightflame" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "A weathered warrior who has seen too much conflict. He now runs a quiet tavern in Capital City, serving as a sanctuary for those seeking redemption." }
          ]
        }
      ]
    },
    tags: ['earth-magic', 'mentor', 'protagonist'],
    wordCount: 89,
    createdAt: '2024-01-15T09:15:00Z',
    updatedAt: '2024-01-16T10:45:00Z'
  },

  'doc-chapter1-789': {
    id: 'doc-chapter1-789',
    projectId: 'project-fantasy-novel',
    title: 'Chapter 1: Awakening',
    path: '/chapters/chapter-01.md',
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
            { "type": "text", "text": "The morning mist clung to the cobblestones of Capital City as Elara made her way through the narrow alleys." }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Her fingers trembled as she felt the familiar warmth building in her chest. The " },
            { "type": "text", "marks": [{ "type": "bold" }], "text": "fire magic" },
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
            { "type": "text", "marks": [{ "type": "italic" }], "text": "Three years ago..." }
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
            { "type": "text", "marks": [{ "type": "italic" }], "text": "screaming" },
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
            { "type": "text", "text": "The tavern door creaked open, and Marcus looked up from behind the bar." }
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
        },
        {
          "type": "blockquote",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "marks": [{ "type": "italic" }], "text": "\"The fire within me burns not for destruction, but for protection. I must learn to control it before it controls me.\"" },
                { "type": "text", "text": " - Elara's journal" }
              ]
            }
          ]
        }
      ]
    },
    tags: ['opening-chapter', 'fire-magic', 'trauma'],
    wordCount: 203,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  },

  'doc-capital-city-321': {
    id: 'doc-capital-city-321',
    projectId: 'project-fantasy-novel',
    title: 'Capital City',
    path: '/locations/settlements/capital-city.md',
    content: {
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": { "level": 1 },
          "content": [{ "type": "text", "text": "Capital City" }]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Overview" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "The largest settlement in the realm, built around the ancient Mage Tower. A sprawling metropolis where magic users hide in plain sight." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Districts" }]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Market Quarter" },
                    { "type": "text", "text": ": Where Marcus runs his tavern" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Noble District" },
                    { "type": "text", "text": ": Home to the ruling council" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Lower City" },
                    { "type": "text", "text": ": Where the common folk live and work" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Notable Locations" }]
        },
        {
          "type": "orderedList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "The Stone Hearth Tavern" },
                    { "type": "text", "text": " - Marcus's establishment" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "The Mage Tower" },
                    { "type": "text", "text": " - Ancient seat of magical learning" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Council Chambers" },
                    { "type": "text", "text": " - Where the city's fate is decided" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "codeBlock",
          "attrs": { "language": null },
          "content": [
            { "type": "text", "text": "Population: ~50,000\nFounded: 847 years ago\nRuler: Council of Seven\nPrimary Trade: Magical artifacts, textiles" }
          ]
        }
      ]
    },
    tags: ['settlement', 'urban', 'politics'],
    wordCount: 95,
    createdAt: '2024-01-15T11:30:00Z',
    updatedAt: '2024-01-16T09:15:00Z'
  },

  'doc-magic-system-999': {
    id: 'doc-magic-system-999',
    projectId: 'project-fantasy-novel',
    title: 'Elemental Magic System',
    path: '/worldbuilding/magic-system.md',
    content: {
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": { "level": 1 },
          "content": [{ "type": "text", "text": "Elemental Magic System" }]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Magic in this world is tied to the four classical elements, with each mage typically having an affinity for one primary element." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "The Four Elements" }]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Fire" },
                    { "type": "text", "text": " - Passion, destruction, transformation" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Earth" },
                    { "type": "text", "text": " - Stability, strength, endurance" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Air" },
                    { "type": "text", "text": " - Freedom, intellect, communication" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "bold" }], "text": "Water" },
                    { "type": "text", "text": " - Emotion, healing, adaptation" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Magic Rules" }]
        },
        {
          "type": "orderedList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "text": "Magic requires emotional connection and intent" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "text": "Overuse leads to exhaustion and potential magical backlash" }
                  ]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "text": "Fear and trauma can cause magic to become unstable" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    tags: ['worldbuilding', 'magic', 'system'],
    wordCount: 156,
    createdAt: '2024-01-15T12:00:00Z',
    updatedAt: '2024-01-16T15:30:00Z'
  }
};

// Project data structure with updated documents
export const mockProjectData: Record<string, ProjectData> = {
  '1': {
    id: '1',
    title: 'My Fantasy Novel',
    description: 'An epic tale of magic, redemption, and unlikely heroes',
    documents: [
      mockDocuments['doc-elara-123'],
      mockDocuments['doc-marcus-456'],
      mockDocuments['doc-chapter1-789'],
      mockDocuments['doc-capital-city-321'],
      mockDocuments['doc-magic-system-999'],
    ],
    fileTree: [
      {
        id: 'folder-characters',
        name: 'characters',
        type: 'folder',
        path: '/characters',
        children: [
          {
            id: 'folder-protagonists',
            name: 'protagonists',
            type: 'folder',
            path: '/characters/protagonists',
            children: [
              {
                id: 'doc-elara-123',
                name: 'Elara Brightflame',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              },
              {
                id: 'doc-marcus-456',
                name: 'Marcus Stonehart',
                type: 'file',
                path: '/characters/protagonists/marcus.md',
                documentId: 'doc-marcus-456',
                tags: ['earth-magic', 'mentor', 'protagonist']
              }
            ]
          }
        ]
      },
      {
        id: 'folder-locations',
        name: 'locations',
        type: 'folder',
        path: '/locations',
        children: [
          {
            id: 'folder-settlements',
            name: 'settlements',
            type: 'folder',
            path: '/locations/settlements',
            children: [
              {
                id: 'doc-capital-city-321',
                name: 'Capital City',
                type: 'file',
                path: '/locations/settlements/capital-city.md',
                documentId: 'doc-capital-city-321',
                tags: ['settlement', 'urban', 'politics']
              }
            ]
          }
        ]
      },
      {
        id: 'folder-chapters',
        name: 'chapters',
        type: 'folder',
        path: '/chapters',
        children: [
          {
            id: 'doc-chapter1-789',
            name: 'Chapter 1: Awakening',
            type: 'file',
            path: '/chapters/chapter-01.md',
            documentId: 'doc-chapter1-789',
            tags: ['opening-chapter', 'fire-magic', 'trauma']
          }
        ]
      },
      {
        id: 'folder-worldbuilding',
        name: 'worldbuilding',
        type: 'folder',
        path: '/worldbuilding',
        children: [
          {
            id: 'doc-magic-system-999',
            name: 'Elemental Magic System',
            type: 'file',
            path: '/worldbuilding/magic-system.md',
            documentId: 'doc-magic-system-999',
            tags: ['worldbuilding', 'magic', 'system']
          }
        ]
      }
    ],
    tags: ['fire-magic', 'earth-magic', 'trauma', 'mentor', 'protagonist', 'settlement', 'urban', 'politics', 'opening-chapter', 'worldbuilding', 'magic', 'system'],
    createdAt: '2024-01-15T08:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  },
  '2': {
    id: '2',
    title: 'Cyberpunk Detective Story',
    description: 'Neon-lit noir in a digital dystopia',
    documents: [
      mockDocuments['doc-elara-123'],
      mockDocuments['doc-marcus-456'],
      mockDocuments['doc-chapter1-789'],
      mockDocuments['doc-capital-city-321'],
      mockDocuments['doc-magic-system-999'],
    ],
    fileTree: [
      {
        id: 'folder-characters-2',
        name: 'characters',
        type: 'folder',
        path: '/characters',
        children: [
          {
            id: 'folder-protagonists-2',
            name: 'protagonists',
            type: 'folder',
            path: '/characters/protagonists',
            children: [
              {
                id: 'doc-elara-123',
                name: 'Elara Brightflame',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              }
            ]
          }
        ]
      }
    ],
    tags: ['cyberpunk', 'noir', 'detective', 'dystopia'],
    createdAt: '2024-01-10T09:15:00Z',
    updatedAt: '2024-01-18T16:45:00Z'
  },
  '3': {
    id: '3',
    title: 'Small Town Mystery',
    description: 'Dark secrets in a peaceful community',
    documents: [
      mockDocuments['doc-elara-123'],
      mockDocuments['doc-marcus-456'],
    ],
    fileTree: [
      {
        id: 'folder-characters-3',
        name: 'characters',
        type: 'folder',
        path: '/characters',
        children: []
      }
    ],
    tags: ['mystery', 'small-town', 'secrets'],
    createdAt: '2024-01-05T11:00:00Z',
    updatedAt: '2024-01-19T13:30:00Z'
  }
};