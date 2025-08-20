/**
 * Development-only content generators for sample data
 * 
 * WHY: Creates varied, realistic content using faker.js with dynamic templates
 * instead of static content. Each generation run produces completely different
 * documents, names, and project structures while maintaining quality.
 * 
 * Enhanced with dynamic markdown templates that are converted to ProseMirror JSON
 * using the markdownToTipTap helper for proper editor display.
 */

import { safeFaker, themeGenerators, getRandomTheme, generateThemeContent } from './faker-utils'
import { 
  generateCharacterTemplate, 
  generateLocationTemplate, 
  generateChapterTemplate,
  generateWorldBuildingTemplate,
  generateResearchTemplate 
} from './dynamic-templates'
import { markdownToTipTap, calculateWordCount } from '../../utils/markdownToTipTap'
import type { Project, Document, FileTreeItem, Tag } from '../../localdb/types'

// Generate random project with theme-appropriate content
export const generateProject = async (userId?: string): Promise<Partial<Project>> => {
  const theme = await getRandomTheme() || 'fantasy'
  const themeData = themeGenerators[theme]
  const helpers = await safeFaker.helpers()
  const lorem = await safeFaker.lorem()
  const date = await safeFaker.date()
  const number = await safeFaker.number()

  const title = await generateThemeContent.projectTitle(theme)
  
  return {
    title,
    description: await lorem.paragraph(),
    ownerId: userId,
    createdBy: userId,
    collaborators: [],
    wordCount: (await number.int({ min: 1000, max: 50000 })),
    documentCount: (await number.int({ min: 5, max: 20 })), // Increased for more variety
    settings: {
      theme,
      autoSave: true,
      wordCountGoal: (await number.int({ min: 50000, max: 200000 })),
      chapterGoal: (await number.int({ min: 10, max: 30 })),
      targetAudience: helpers.arrayElement(['Young Adult', 'Adult', 'Middle Grade', 'General Audience']),
      genre: theme === 'fantasy' 
        ? helpers.arrayElement(['Epic Fantasy', 'Urban Fantasy', 'Dark Fantasy', 'High Fantasy', 'Magical Realism'])
        : theme === 'scifi'
        ? helpers.arrayElement(['Space Opera', 'Cyberpunk', 'Hard Sci-Fi', 'Dystopian', 'Time Travel'])
        : theme === 'mystery'
        ? helpers.arrayElement(['Cozy Mystery', 'Police Procedural', 'Noir', 'Thriller', 'Detective Fiction'])
        : helpers.arrayElement(['Contemporary Fiction', 'Literary Fiction', 'Drama', 'Slice of Life', 'Social Commentary'])
    },
    tags: helpers.arrayElements(themeData.tags, (await number.int({ min: 2, max: 5 }))),
    createdAt: (await date.past()).toISOString(),
    updatedAt: (await date.recent()).toISOString()
  }
}

// Generate character document with dynamic content
export const generateCharacter = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()
  const helpers = await safeFaker.helpers()

  const characterName = await generateThemeContent.characterName(theme)
  const fileName = `${characterName.toLowerCase().replace(/\s+/g, '-')}.md`
  const path = `/characters/${fileName}`

  // Generate rich markdown content using dynamic template
  const markdownContent = await generateCharacterTemplate(theme)
  
  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: characterName,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'character', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'User',
      tags: [theme, 'character', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate location document with dynamic content
export const generateLocation = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()

  const locationName = await generateThemeContent.locationName(theme)
  const fileName = `${locationName.toLowerCase().replace(/\s+/g, '-')}.md`
  const path = `/locations/${fileName}`

  // Generate rich markdown content using dynamic template
  const markdownContent = await generateLocationTemplate(theme)
  
  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: locationName,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'location', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'MapPin',
      tags: [theme, 'location', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate chapter document with dynamic content
export const generateChapter = async (theme: keyof typeof themeGenerators, projectId: string, chapterNumber: number, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()

  const chapterTitle = await generateThemeContent.chapterTitle(theme, chapterNumber)
  const fileName = `chapter-${chapterNumber.toString().padStart(2, '0')}.md`
  const path = `/chapters/${fileName}`

  // Generate rich markdown content using dynamic template
  const markdownContent = await generateChapterTemplate(theme, chapterNumber)
  
  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: chapterTitle,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'chapter', 'story', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'BookOpen',
      tags: [theme, 'chapter', 'story', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate theme-appropriate tags
export const generateTags = async (theme: keyof typeof themeGenerators, projectId?: string): Promise<Partial<Tag>[]> => {
  const themeData = themeGenerators[theme]
  const helpers = await safeFaker.helpers()
  const date = await safeFaker.date()
  const number = await safeFaker.number()

  const colors = ['#ff6b6b', '#4ecdc4', '#95a5a6', '#f39c12', '#9b59b6', '#2ecc71', '#e74c3c', '#3498db']
  const icons = ['Flame', 'Star', 'Book', 'Play', 'Home', 'Heart', 'Sword', 'Shield']

  const tagPromises = themeData.tags.map(async (tagName, index) => ({
    projectId,
    name: tagName,
    category: theme,
    color: helpers.arrayElement(colors) || '#95a5a6',
    icon: helpers.arrayElement(icons) || 'Star',
    description: `${tagName.charAt(0).toUpperCase() + tagName.slice(1)} related content`,
    isGlobal: false,
    isSystem: false,
    isArchived: false,
    usageCount: await number.int({ min: 1, max: 10 }),
    createdAt: (await date.past()).toISOString(),
    updatedAt: new Date().toISOString()
  }))
  
  return await Promise.all(tagPromises)
}

// Generate world-building document (magic system, technology, etc.)
export const generateWorldBuildingDocument = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()
  const helpers = await safeFaker.helpers()

  const documentType = theme === 'fantasy' ? 'magic' : theme === 'scifi' ? 'technology' : 'system'
  const documentName = theme === 'fantasy' 
    ? helpers.arrayElement(['Magic System', 'Ancient Lore', 'Divine Powers', 'Elemental Forces', 'Arcane Arts']) || 'Magic System'
    : theme === 'scifi'
    ? helpers.arrayElement(['Technology Overview', 'Scientific Principles', 'AI Systems', 'Space Travel', 'Quantum Mechanics']) || 'Technology Overview'
    : theme === 'mystery'
    ? helpers.arrayElement(['Investigation Methods', 'Forensic Procedures', 'Legal System', 'Criminal Psychology']) || 'Investigation Methods'
    : helpers.arrayElement(['Social Systems', 'Cultural Framework', 'Organizational Structure']) || 'Social Systems'

  const fileName = `${documentName.toLowerCase().replace(/\s+/g, '-')}.md`
  const path = `/world-building/${fileName}`

  // Generate rich markdown content using dynamic template
  const markdownContent = await generateWorldBuildingTemplate(theme, documentType)
  
  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: documentName,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'worldbuilding', 'reference', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'Globe',
      tags: [theme, 'worldbuilding', 'reference', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate research document
export const generateResearchDocument = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()
  const helpers = await safeFaker.helpers()

  const researchTopic = theme === 'fantasy' 
    ? helpers.arrayElement(['Ancient History', 'Mythology Research', 'Medieval Culture', 'Magical Practices', 'Historical Battles']) || 'Ancient History'
    : theme === 'scifi'
    ? helpers.arrayElement(['Space Exploration', 'Future Technology', 'Scientific Discoveries', 'Alien Cultures', 'Quantum Physics']) || 'Space Exploration'
    : theme === 'mystery'
    ? helpers.arrayElement(['Criminal Cases', 'Investigation Techniques', 'Forensic Science', 'Legal Procedures', 'Psychology Studies']) || 'Criminal Cases'
    : helpers.arrayElement(['Social Research', 'Cultural Studies', 'Current Events', 'Human Behavior', 'Technology Impact']) || 'Social Research'

  const fileName = `${researchTopic.toLowerCase().replace(/\s+/g, '-')}-research.md`
  const path = `/research/${fileName}`

  // Generate rich markdown content using dynamic template
  const markdownContent = await generateResearchTemplate(theme)
  
  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: `${researchTopic} Research`,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'research', 'notes', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'Search',
      tags: [theme, 'research', 'notes', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate timeline document
export const generateTimelineDocument = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const date = await safeFaker.date()
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()

  const timelineTitle = theme === 'fantasy' 
    ? helpers.arrayElement(['Kingdom Timeline', 'War Chronology', 'Magical Events', 'Dynasty History', 'Prophecy Timeline']) || 'Kingdom Timeline'
    : theme === 'scifi'
    ? helpers.arrayElement(['Galactic History', 'Technology Timeline', 'Colonial Expansion', 'First Contact Events', 'Scientific Milestones']) || 'Galactic History'
    : theme === 'mystery'
    ? helpers.arrayElement(['Case Timeline', 'Investigation Chronology', 'Crime Sequence', 'Evidence Timeline', 'Suspect Activities']) || 'Case Timeline'
    : helpers.arrayElement(['Project Timeline', 'Historical Events', 'Development Milestones', 'Cultural Timeline', 'Personal History']) || 'Project Timeline'

  const fileName = `${timelineTitle.toLowerCase().replace(/\s+/g, '-')}.md`
  const path = `/timeline/${fileName}`

  // Generate timeline markdown content
  const events = await Promise.all(Array.from({length: await number.int({ min: 5, max: 12 })}, async (_, i) => {
    const year = theme === 'fantasy' 
      ? await number.int({ min: 1000, max: 1500 })
      : theme === 'scifi'
      ? await number.int({ min: 2100, max: 3000 })
      : await number.int({ min: 1990, max: 2025 })
    
    const eventName = theme === 'fantasy'
      ? helpers.arrayElement(['The Great War', 'Dragon Awakening', 'Magic Discovery', 'Kingdom Founded', 'Prophecy Fulfilled', 'Ancient Curse']) || 'Significant Event'
      : theme === 'scifi'
      ? helpers.arrayElement(['First Contact', 'Colony Established', 'AI Breakthrough', 'Warp Drive Invented', 'Alien Alliance', 'Galactic War']) || 'Major Discovery'
      : theme === 'mystery'
      ? helpers.arrayElement(['Crime Committed', 'Evidence Found', 'Suspect Identified', 'Witness Interview', 'Arrest Made', 'Trial Begins']) || 'Investigation Step'
      : helpers.arrayElement(['Project Launch', 'Major Milestone', 'System Update', 'Team Expansion', 'Partnership Formed', 'Achievement Unlocked']) || 'Important Event'
    
    return { year, event: eventName, description: await lorem.sentence() }
  }))

  events.sort((a, b) => a.year - b.year)

  const markdownContent = `# ${timelineTitle}

## Overview

${await lorem.paragraph()}

---

## Timeline of Events

${events.map(event => `### ${event.year}: ${event.event}

${event.description}

---`).join('\n\n')}

## Analysis

${await lorem.paragraph()}

### Key Patterns
- **${helpers.arrayElement(['Cyclical Events', 'Escalating Tensions', 'Technological Progress', 'Cultural Shifts'])}**: ${await lorem.sentence()}
- **${helpers.arrayElement(['Major Turning Points', 'Influential Figures', 'Unexpected Developments', 'Long-term Consequences'])}**: ${await lorem.sentence()}

### Future Implications
${await lorem.paragraph()}

**Timeline Created**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Status**: ${helpers.arrayElement(['Active', 'Complete', 'In Progress', 'Under Review'])}`

  // Convert markdown to ProseMirror format
  const content = markdownToTipTap(markdownContent)
  const wordCount = calculateWordCount(content)

  const now = new Date().toISOString()
  const tags = await generateThemeContent.getThemeSpecificTags(theme)

  return {
    document: {
      projectId,
      path,
      title: timelineTitle,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'timeline', 'chronology', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now,
      content
    },
    fileTree: {
      projectId,
      name: fileName,
      type: 'file' as const,
      path,
      parentId,
      wordCount,
      icon: 'Clock',
      tags: [theme, 'timeline', 'chronology', ...tags],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}