export interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  children?: FileItem[];
  tags?: string[];
}

export const mockFileTree: FileItem[] = [
  {
    id: "1",
    name: "characters",
    type: "folder",
    children: [
      {
        id: "2",
        name: "protagonists",
        type: "folder",
        children: [
          { id: "3", name: "elara.md", type: "file", tags: ["fire-magic", "trauma"] },
          { id: "4", name: "marcus.md", type: "file", tags: ["earth-magic", "mentor"] },
        ],
      },
      {
        id: "5",
        name: "antagonists",
        type: "folder",
        children: [
          { id: "6", name: "shadow-lord.md", type: "file", tags: ["dark-magic", "villain"] },
        ],
      },
    ],
  },
  {
    id: "7",
    name: "locations",
    type: "folder",
    children: [
      { id: "8", name: "capital-city.md", type: "file", tags: ["urban", "politics"] },
      { id: "9", name: "ancient-temple.md", type: "file", tags: ["mystical", "ruins"] },
    ],
  },
  {
    id: "10",
    name: "timeline",
    type: "folder",
    children: [
      { id: "11", name: "main-story.md", type: "file" },
      { id: "12", name: "backstory.md", type: "file" },
    ],
  },
  {
    id: "13",
    name: "chapters",
    type: "folder",
    children: [
      { id: "14", name: "chapter-01.md", type: "file" },
      { id: "15", name: "chapter-02.md", type: "file" },
      { id: "16", name: "chapter-03.md", type: "file" },
    ],
  },
];

export function findFileById(id: string, items: FileItem[] = mockFileTree): FileItem | undefined {
  for (const item of items) {
    if (item.id === id) {
      return item;
    }
    if (item.children) {
      const found = findFileById(id, item.children);
      if (found) return found;
    }
  }
  return undefined;
}