import { ProjectCollaborator } from '@/types/api';

export interface Project {
  id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
  document_count: number;
  word_count: number;
  collaborators: ProjectCollaborator[];
  tags: string[];
  genre?: string;
}

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

export const mockProjects: Project[] = [
  {
    id: "1",
    title: "The Chronicles of Elara",
    description: "A fantasy epic about a young mage discovering her powers in a world where magic is forbidden.",
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-20T14:22:00Z",
    document_count: 23,
    word_count: 45230,
    collaborators: [
      {
        user_id: "user-1",
        role: "owner",
        name: "You",
        avatar: null
      }
    ],
    tags: ["Fantasy", "Magic", "Coming of Age"],
    genre: "Fantasy"
  },
  {
    id: "2", 
    title: "Cyberpunk Nights",
    description: "A noir detective story set in a neon-lit future where corporate espionage meets street justice.",
    created_at: "2024-01-10T09:15:00Z",
    updated_at: "2024-01-18T16:45:00Z",
    document_count: 15,
    word_count: 28750,
    collaborators: [
      {
        user_id: "user-1",
        role: "owner",
        name: "You",
        avatar: null
      },
      {
        user_id: "user-2",
        role: "editor",
        name: "Alex Chen",
        avatar: null
      }
    ],
    tags: ["Sci-Fi", "Noir", "Cyberpunk"],
    genre: "Sci-Fi"
  },
  {
    id: "3",
    title: "Small Town Secrets",
    description: "A contemporary mystery exploring the dark underbelly of a seemingly peaceful suburban community.",
    created_at: "2024-01-05T11:00:00Z", 
    updated_at: "2024-01-19T13:30:00Z",
    document_count: 8,
    word_count: 12400,
    collaborators: [
      {
        user_id: "user-1",
        role: "owner",
        name: "You",
        avatar: null
      }
    ],
    tags: ["Mystery", "Contemporary", "Small Town"],
    genre: "Mystery"
  }
];

export function getProjectById(id: string): Project | undefined {
  return mockProjects.find(project => project.id === id);
}

export function getProjectDisplayData(projectId: string) {
  const project = getProjectById(projectId);
  return {
    id: projectId,
    title: project?.title ?? 
           (projectId === "1" ? "The Chronicles of Elara" : 
            projectId === "2" ? "Cyberpunk Nights" :
            projectId === "3" ? "Small Town Secrets" : "New Project"),
    wordCount: project?.word_count ?? 45230
  };
}