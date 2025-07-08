export interface AiMode {
  value: string;
  label: string;
  icon: string;
}

export interface ContextItem {
  type: "character" | "location" | "tag";
  name: string;
  description: string;
}

export const aiModes: AiMode[] = [
  { value: "writing", label: "Chapter Writing", icon: "✍️" },
  { value: "character", label: "Character Development", icon: "👥" },
  { value: "worldbuilding", label: "World Building", icon: "🌍" },
  { value: "plot", label: "Plot Planning", icon: "📋" },
  { value: "dialogue", label: "Dialogue Polish", icon: "💬" },
];

export const mockContext: ContextItem[] = [
  { type: "character", name: "elara", description: "Fire magic user, trauma survivor" },
  { type: "location", name: "capital-city", description: "Urban setting, political intrigue" },
  { type: "tag", name: "fire-magic", description: "Elemental magic system" },
];

export function getAiModeById(value: string): AiMode | undefined {
  return aiModes.find(mode => mode.value === value);
}