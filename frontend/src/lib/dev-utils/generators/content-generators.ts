/**
 * Development-only content generators for sample data
 * Uses faker.js to create varied, realistic content
 */

import { safeFaker, themeGenerators, getRandomTheme } from './faker-utils'
import type { Project, Document, FileTreeItem, Tag } from '../../localdb/types'

// Generate random project with theme-appropriate content
export const generateProject = async (userId?: string): Promise<Partial<Project>> => {
  const theme = await getRandomTheme() || 'fantasy'
  const themeData = themeGenerators[theme]
  const helpers = await safeFaker.helpers()
  const lorem = await safeFaker.lorem()
  const date = await safeFaker.date()
  const number = await safeFaker.number()

  const titlePrefix = helpers.arrayElement(themeData.titles) || 'Tales of'
  const titleSuffix = helpers.arrayElement(themeData.places) || 'Adventure'
  
  return {
    title: `${titlePrefix} ${titleSuffix}`,
    description: await lorem.paragraph(),
    ownerId: userId,
    createdBy: userId,
    collaborators: [],
    wordCount: (await number.int({ min: 1000, max: 50000 })),
    documentCount: (await number.int({ min: 3, max: 15 })),
    settings: {
      theme,
      autoSave: true,
      wordCountGoal: (await number.int({ min: 50000, max: 200000 }))
    },
    tags: helpers.arrayElements(themeData.tags, (await number.int({ min: 2, max: 4 }))),
    createdAt: (await date.past()).toISOString(),
    updatedAt: (await date.recent()).toISOString()
  }
}

// Generate character document
export const generateCharacter = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const themeData = themeGenerators[theme]
  const person = await safeFaker.person()
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const characterName = helpers.arrayElement(themeData.characters) || 'Character'
  const lastName = await person.lastName()
  const fullName = `${characterName} ${lastName}`
  const fileName = `${characterName.toLowerCase()}.md`
  const path = `/characters/${fileName}`

  const abilities = theme === 'fantasy' 
    ? ['Magic wielding', 'Swordsmanship', 'Healing powers', 'Beast taming', 'Elemental control']
    : theme === 'scifi' 
    ? ['Cybernetic enhancement', 'Quantum computing', 'Zero-g navigation', 'AI interfacing', 'Energy manipulation']
    : ['Investigation skills', 'Deductive reasoning', 'Combat training', 'Psychological profiling', 'Forensic analysis']

  const content = {
    type: 'doc',
    content: [
      {
        type: 'heading',
        attrs: { level: 1 },
        content: [{ type: 'text', text: fullName }]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.sentence() }
        ]
      },
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'Background' }]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.paragraph() }
        ]
      },
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'Abilities' }]
      },
      {
        type: 'bulletList',
        content: helpers.arrayElements(abilities, 3).map(ability => ({
          type: 'listItem',
          content: [{
            type: 'paragraph',
            content: [{ type: 'text', text: ability }]
          }]
        }))
      }
    ]
  }

  const now = new Date().toISOString()
  const wordCount = await number.int({ min: 150, max: 800 })

  return {
    document: {
      projectId,
      path,
      title: fullName,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'character'],
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
      tags: [theme, 'character'],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate location document  
export const generateLocation = async (theme: keyof typeof themeGenerators, projectId: string, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const themeData = themeGenerators[theme]
  const location = await safeFaker.location()
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const placeName = helpers.arrayElement(themeData.places) || 'Unknown Place'
  const fileName = `${placeName.toLowerCase().replace(/\s+/g, '-')}.md`
  const path = `/locations/${fileName}`

  const features = theme === 'fantasy' 
    ? ['Ancient ruins', 'Mystical forests', 'Crystal caves', 'Dragon lairs', 'Magical springs']
    : theme === 'scifi' 
    ? ['Orbital platforms', 'Quantum laboratories', 'Terraforming stations', 'Hyperspace gates', 'AI cores']
    : ['Crime scenes', 'Police stations', 'Witness locations', 'Evidence rooms', 'Suspect hideouts']

  const content = {
    type: 'doc',
    content: [
      {
        type: 'heading',
        attrs: { level: 1 },
        content: [{ type: 'text', text: placeName }]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.paragraph() }
        ]
      },
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'Notable Features' }]
      },
      {
        type: 'bulletList',
        content: helpers.arrayElements(features, 3).map(feature => ({
          type: 'listItem',
          content: [{
            type: 'paragraph',
            content: [{ type: 'text', text: feature }]
          }]
        }))
      }
    ]
  }

  const now = new Date().toISOString()
  const wordCount = await number.int({ min: 100, max: 600 })

  return {
    document: {
      projectId,
      path,
      title: placeName,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'location'],
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
      tags: [theme, 'location'],
      createdAt: (await date.past()).toISOString(),
      updatedAt: now
    }
  }
}

// Generate chapter document
export const generateChapter = async (theme: keyof typeof themeGenerators, projectId: string, chapterNumber: number, parentId?: string): Promise<{
  document: Partial<Document>,
  fileTree: Partial<FileTreeItem>
}> => {
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const chapterTitles = theme === 'fantasy' 
    ? ['The Awakening', 'Quest Begins', 'Dark Forest', 'Dragon\'s Lair', 'Magic Revealed', 'Battle of Storms']
    : theme === 'scifi' 
    ? ['First Contact', 'The Discovery', 'Quantum Leap', 'AI Uprising', 'Deep Space', 'Final Protocol']
    : ['The Crime', 'First Clues', 'The Investigation', 'Hidden Motives', 'The Chase', 'Truth Revealed']

  const title = `Chapter ${chapterNumber}: ${helpers.arrayElement(chapterTitles) || 'The Story'}`
  const fileName = `chapter-${chapterNumber}.md`
  const path = `/chapters/${fileName}`

  const content = {
    type: 'doc',
    content: [
      {
        type: 'heading',
        attrs: { level: 1 },
        content: [{ type: 'text', text: title }]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.paragraph() }
        ]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.paragraph() }
        ]
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: await lorem.sentence() }
        ]
      }
    ]
  }

  const now = new Date().toISOString()
  const wordCount = await number.int({ min: 800, max: 2500 })

  return {
    document: {
      projectId,
      path,
      title,
      version: '1.0.0',
      isLocked: false,
      wordCount,
      tags: [theme, 'chapter', 'story'],
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
      icon: 'FileText',
      tags: [theme, 'chapter', 'story'],
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