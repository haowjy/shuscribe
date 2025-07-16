export interface ProjectTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  folders: string[];
  genre: string;
}

export const projectTemplates: ProjectTemplate[] = [
  {
    id: "fantasy",
    name: "Fantasy Novel",
    description: "Epic fantasy with characters, locations, magic systems, and world-building",
    icon: "✨",
    folders: ["Characters", "Locations", "Magic System", "Timeline", "Chapters"],
    genre: "Fantasy"
  },
  {
    id: "mystery",
    name: "Mystery/Thriller",
    description: "Crime fiction with suspects, clues, timeline, and investigation notes",
    icon: "🔍",
    folders: ["Characters", "Locations", "Evidence", "Timeline", "Chapters"],
    genre: "Mystery"
  },
  {
    id: "scifi",
    name: "Science Fiction",
    description: "Sci-fi with technology, world-building, characters, and future concepts",
    icon: "🚀",
    folders: ["Characters", "Locations", "Technology", "Timeline", "Chapters"],
    genre: "Sci-Fi"
  },
  {
    id: "romance",
    name: "Romance",
    description: "Romance novel with character development, relationships, and emotional arcs",
    icon: "💕",
    folders: ["Characters", "Locations", "Relationships", "Timeline", "Chapters"],
    genre: "Romance"
  },
  {
    id: "general",
    name: "General Fiction",
    description: "Flexible structure for any genre or writing style",
    icon: "📚",
    folders: ["Characters", "Locations", "Notes", "Timeline", "Chapters"],
    genre: "Fiction"
  },
  {
    id: "blank",
    name: "Blank Project",
    description: "Start from scratch with no predefined structure",
    icon: "📝",
    folders: [],
    genre: ""
  }
];