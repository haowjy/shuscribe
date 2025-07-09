// Mock API data with proper UUIDs and project structure

import { Document, ProjectData, FileItem } from '@/types/project';

// Document storage
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
          "type": "bullet_list",
          "content": [
            {
              "type": "list_item",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Age" },
                    { "type": "text", "text": ": 45" }
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
                    { "type": "text", "text": ": Earth elemental" }
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
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Role" },
                    { "type": "text", "text": ": Mentor to " },
                    { "type": "reference", "attrs": { "reference": "characters/protagonists/elara", "type": "character" } }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "A weathered warrior who has seen too much conflict. He now runs a quiet tavern in " },
            { "type": "reference", "attrs": { "reference": "locations/capital-city", "type": "location" } },
            { "type": "text", "text": ", serving as a sanctuary for those seeking redemption." }
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
            { "type": "text", "text": "The largest settlement in the realm, built around the ancient " },
            { "type": "reference", "attrs": { "reference": "locations/mystical/mage-tower", "type": "location" } },
            { "type": "text", "text": ". A sprawling metropolis where magic users hide in plain sight." }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 2 },
          "content": [{ "type": "text", "text": "Districts" }]
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
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Market Quarter" },
                    { "type": "text", "text": ": Where " },
                    { "type": "reference", "attrs": { "reference": "characters/protagonists/marcus", "type": "character" } },
                    { "type": "text", "text": " runs his tavern" }
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
                    { "type": "text", "marks": [{ "type": "strong" }], "text": "Noble District" },
                    { "type": "text", "text": ": Home to the ruling council" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    tags: ['settlement', 'urban', 'politics'],
    wordCount: 95,
    createdAt: '2024-01-15T11:30:00Z',
    updatedAt: '2024-01-16T09:15:00Z'
  }
};

// Project data structure
export const mockProjectData: Record<string, ProjectData> = {
  '1': {
    id: '1',
    title: 'My Fantasy Novel',
    description: 'An epic tale of magic, redemption, and unlikely heroes',
    documents: Object.values(mockDocuments),
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
                id: 'file-elara',
                name: 'elara.md',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              },
              {
                id: 'file-marcus',
                name: 'marcus.md',
                type: 'file',
                path: '/characters/protagonists/marcus.md',
                documentId: 'doc-marcus-456',
                tags: ['earth-magic', 'mentor', 'protagonist']
              }
            ]
          },
          {
            id: 'folder-antagonists',
            name: 'antagonists',
            type: 'folder',
            path: '/characters/antagonists',
            children: []
          },
          {
            id: 'folder-supporting',
            name: 'supporting',
            type: 'folder',
            path: '/characters/supporting',
            children: []
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
                id: 'file-capital-city',
                name: 'capital-city.md',
                type: 'file',
                path: '/locations/settlements/capital-city.md',
                documentId: 'doc-capital-city-321',
                tags: ['settlement', 'urban', 'politics']
              }
            ]
          },
          {
            id: 'folder-mystical',
            name: 'mystical',
            type: 'folder',
            path: '/locations/mystical',
            children: []
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
            id: 'file-chapter1',
            name: 'chapter-01.md',
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
        children: []
      }
    ],
    tags: ['fire-magic', 'earth-magic', 'trauma', 'mentor', 'protagonist', 'settlement', 'urban', 'politics', 'opening-chapter'],
    createdAt: '2024-01-15T08:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  },
  '2': {
    id: '2',
    title: 'My Fantasy Novel',
    description: 'An epic tale of magic, redemption, and unlikely heroes',
    documents: Object.values(mockDocuments),
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
                id: 'file-elara',
                name: 'elara.md',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              },
              {
                id: 'file-marcus',
                name: 'marcus.md',
                type: 'file',
                path: '/characters/protagonists/marcus.md',
                documentId: 'doc-marcus-456',
                tags: ['earth-magic', 'mentor', 'protagonist']
              }
            ]
          },
          {
            id: 'folder-antagonists',
            name: 'antagonists',
            type: 'folder',
            path: '/characters/antagonists',
            children: []
          },
          {
            id: 'folder-supporting',
            name: 'supporting',
            type: 'folder',
            path: '/characters/supporting',
            children: []
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
                id: 'file-capital-city',
                name: 'capital-city.md',
                type: 'file',
                path: '/locations/settlements/capital-city.md',
                documentId: 'doc-capital-city-321',
                tags: ['settlement', 'urban', 'politics']
              }
            ]
          },
          {
            id: 'folder-mystical',
            name: 'mystical',
            type: 'folder',
            path: '/locations/mystical',
            children: []
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
            id: 'file-chapter1',
            name: 'chapter-01.md',
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
        children: []
      }
    ],
    tags: ['fire-magic', 'earth-magic', 'trauma', 'mentor', 'protagonist', 'settlement', 'urban', 'politics', 'opening-chapter'],
    createdAt: '2024-01-15T08:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  },
  '3': {
    id: '3',
    title: 'My Fantasy Novel',
    description: 'An epic tale of magic, redemption, and unlikely heroes',
    documents: Object.values(mockDocuments),
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
                id: 'file-elara',
                name: 'elara.md',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              },
              {
                id: 'file-marcus',
                name: 'marcus.md',
                type: 'file',
                path: '/characters/protagonists/marcus.md',
                documentId: 'doc-marcus-456',
                tags: ['earth-magic', 'mentor', 'protagonist']
              }
            ]
          },
          {
            id: 'folder-antagonists',
            name: 'antagonists',
            type: 'folder',
            path: '/characters/antagonists',
            children: []
          },
          {
            id: 'folder-supporting',
            name: 'supporting',
            type: 'folder',
            path: '/characters/supporting',
            children: []
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
                id: 'file-capital-city',
                name: 'capital-city.md',
                type: 'file',
                path: '/locations/settlements/capital-city.md',
                documentId: 'doc-capital-city-321',
                tags: ['settlement', 'urban', 'politics']
              }
            ]
          },
          {
            id: 'folder-mystical',
            name: 'mystical',
            type: 'folder',
            path: '/locations/mystical',
            children: []
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
            id: 'file-chapter1',
            name: 'chapter-01.md',
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
        children: []
      }
    ],
    tags: ['fire-magic', 'earth-magic', 'trauma', 'mentor', 'protagonist', 'settlement', 'urban', 'politics', 'opening-chapter'],
    createdAt: '2024-01-15T08:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  },
  'project-fantasy-novel': {
    id: 'project-fantasy-novel',
    title: 'My Fantasy Novel',
    description: 'An epic tale of magic, redemption, and unlikely heroes',
    documents: Object.values(mockDocuments),
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
                id: 'file-elara',
                name: 'elara.md',
                type: 'file',
                path: '/characters/protagonists/elara.md',
                documentId: 'doc-elara-123',
                tags: ['fire-magic', 'trauma', 'protagonist']
              },
              {
                id: 'file-marcus',
                name: 'marcus.md',
                type: 'file',
                path: '/characters/protagonists/marcus.md',
                documentId: 'doc-marcus-456',
                tags: ['earth-magic', 'mentor', 'protagonist']
              }
            ]
          },
          {
            id: 'folder-antagonists',
            name: 'antagonists',
            type: 'folder',
            path: '/characters/antagonists',
            children: []
          },
          {
            id: 'folder-supporting',
            name: 'supporting',
            type: 'folder',
            path: '/characters/supporting',
            children: []
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
                id: 'file-capital-city',
                name: 'capital-city.md',
                type: 'file',
                path: '/locations/settlements/capital-city.md',
                documentId: 'doc-capital-city-321',
                tags: ['settlement', 'urban', 'politics']
              }
            ]
          },
          {
            id: 'folder-mystical',
            name: 'mystical',
            type: 'folder',
            path: '/locations/mystical',
            children: []
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
            id: 'file-chapter1',
            name: 'chapter-01.md',
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
        children: []
      }
    ],
    tags: ['fire-magic', 'earth-magic', 'trauma', 'mentor', 'protagonist', 'settlement', 'urban', 'politics', 'opening-chapter'],
    createdAt: '2024-01-15T08:00:00Z',
    updatedAt: '2024-01-17T16:30:00Z'
  }
};