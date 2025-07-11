export interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  children?: FileItem[];
  tags?: string[];
  icon?: string; // Icon name for the file/folder
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
          { id: "3", name: "elara.md", type: "file", tags: ["fire-magic", "trauma"], icon: "User" },
          { id: "4", name: "marcus.md", type: "file", tags: ["earth-magic", "mentor"], icon: "User" },
        ],
      },
      {
        id: "5",
        name: "antagonists",
        type: "folder",
        children: [
          { id: "6", name: "shadow-lord.md", type: "file", tags: ["dark-magic", "villain"], icon: "Skull" },
        ],
      },
    ],
  },
  {
    id: "7",
    name: "locations",
    type: "folder",
    children: [
      { id: "8", name: "capital-city.md", type: "file", tags: ["urban", "politics"], icon: "Building" },
      { id: "9", name: "ancient-temple.md", type: "file", tags: ["mystical", "ruins"], icon: "Landmark" },
    ],
  },
  {
    id: "10",
    name: "timeline",
    type: "folder",
    children: [
      { id: "11", name: "main-story.md", type: "file", icon: "Clock" },
      { id: "12", name: "backstory.md", type: "file", icon: "History" },
    ],
  },
  {
    id: "13",
    name: "chapters",
    type: "folder",
    children: [
      { id: "14", name: "chapter-01.md", type: "file", icon: "BookOpen" },
      { id: "15", name: "chapter-02.md", type: "file", icon: "BookOpen" },
      { id: "16", name: "chapter-03.md", type: "file", icon: "BookOpen" },
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