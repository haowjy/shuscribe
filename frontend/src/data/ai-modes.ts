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


export function getAiModeById(value: string): AiMode | undefined {
  return aiModes.find(mode => mode.value === value);
}