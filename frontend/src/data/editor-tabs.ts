export interface EditorTab {
  id: string;
  name: string;
  content: string;
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
    content: `# Elara Brightflame

## Character Profile
- **Age**: 23
- **Magic**: Fire elemental
- **Background**: Noble-born, but haunted by trauma

## Personality
Elara is cautious about using her powers after accidentally burning down her childhood home. She's been suppressing her abilities for three years, but recent events may force her to embrace them again.

## Relationships
- **@characters/protagonists/marcus**: Her mentor and guide
- **@locations/capital-city**: Where she currently lives in exile`,
    isDirty: false,
    order: 0,
  },
  {
    id: "2",
    name: "chapter-01.md",
    filePath: "chapters/chapter-01.md",
    content: `# Chapter 1: Awakening

The morning mist clung to the cobblestones of @locations/capital-city as @characters/protagonists/elara made her way through the narrow alleys. She had been hiding for three years, but today everything would change.

Her fingers trembled as she felt the familiar warmth building in her chest. The @fire-magic that had once consumed her childhood home was stirring again, and this time she couldn't run from it.`,
    isDirty: false,
    order: 1,
  },
];

export function getTabById(id: string): EditorTab | undefined {
  return mockTabs.find(tab => tab.id === id);
}