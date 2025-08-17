/**
 * Development-only faker utilities
 * This file should NEVER be imported in production code paths
 */

// Safe conditional faker import - only in development
export const getFaker = async () => {
  if (process.env.NODE_ENV === 'development') {
    try {
      const { faker } = await import('@faker-js/faker')
      return faker
    } catch (error) {
      console.warn('Faker.js not available in development:', error)
      return null
    }
  }
  return null
}

// Development environment check
export const isDevelopment = () => process.env.NODE_ENV === 'development'

// Safe faker wrapper that returns fallback values in production
export const safeFaker = {
  async person() {
    const faker = await getFaker()
    if (!faker) return {
      fullName: () => 'Character Name',
      firstName: () => 'First',
      lastName: () => 'Last',
      jobTitle: () => 'Adventurer'
    }
    return faker.person
  },

  async location() {
    const faker = await getFaker()
    if (!faker) return {
      city: () => 'City',
      country: () => 'Kingdom',
      buildingNumber: () => '1',
      street: () => 'Main Street'
    }
    return faker.location
  },

  async lorem() {
    const faker = await getFaker()
    if (!faker) return {
      sentence: () => 'A sample sentence.',
      paragraph: () => 'A sample paragraph with some text.',
      words: () => ['sample', 'words'],
      slug: () => 'sample-slug'
    }
    return faker.lorem
  },

  async date() {
    const faker = await getFaker()
    if (!faker) return {
      recent: () => new Date(),
      past: () => new Date(Date.now() - 86400000), // Yesterday
      between: () => new Date()
    }
    return faker.date
  },

  async number() {
    const faker = await getFaker()
    if (!faker) return {
      int: () => Math.floor(Math.random() * 100),
      float: () => Math.random() * 100
    }
    return faker.number
  },

  async helpers() {
    const faker = await getFaker()
    if (!faker) return {
      arrayElement: <T>(arr: T[]) => arr[0] || null,
      arrayElements: <T>(arr: T[]) => arr.slice(0, 2),
      shuffle: <T>(arr: T[]) => [...arr]
    }
    return faker.helpers
  }
}

// Theme-specific generators
export const themeGenerators = {
  fantasy: {
    places: ['Stormwind', 'Ironforge', 'Shadowmere', 'Dragonspire', 'Moonhaven', 'Thornwood', 'Silverpeak', 'Ravenshollow'],
    characters: ['Elara', 'Theron', 'Lyanna', 'Gareth', 'Seraphina', 'Draven', 'Aria', 'Kael'],
    titles: ['Epic Fantasy', 'The Chronicles of', 'Legends of', 'Tales from', 'The Saga of', 'Adventures in'],
    tags: ['fantasy', 'magic', 'dragons', 'medieval', 'quest', 'adventure', 'epic']
  },
  scifi: {
    places: ['New Terra', 'Quantum Station', 'Nebula Prime', 'Starport Alpha', 'Cybercity', 'Mars Colony', 'Deep Space Nine'],
    characters: ['Zara', 'Rex', 'Nova', 'Cipher', 'Echo', 'Phoenix', 'Vega', 'Orion'],
    titles: ['Space Chronicles', 'Galactic', 'Stellar', 'Cosmic', 'Future', 'Quantum'],
    tags: ['sci-fi', 'space', 'future', 'technology', 'aliens', 'robots', 'cyberpunk']
  },
  mystery: {
    places: ['Blackwater', 'Foggy Hollow', 'Old Town', 'The Manor', 'Riverside', 'Millbrook', 'Crescent Bay'],
    characters: ['Detective Morgan', 'Inspector Vale', 'Sarah Chen', 'Marcus Webb', 'Diana Cross', 'Jack Sterling'],
    titles: ['Mystery of', 'The Case of', 'Murder at', 'Secrets of', 'The Disappearance of', 'Death in'],
    tags: ['mystery', 'crime', 'detective', 'thriller', 'investigation', 'murder', 'suspense']
  }
}

// Get random theme
export const getRandomTheme = async (): Promise<keyof typeof themeGenerators> => {
  const helpers = await safeFaker.helpers()
  const themes = Object.keys(themeGenerators) as Array<keyof typeof themeGenerators>
  return helpers.arrayElement(themes) || 'fantasy'
}