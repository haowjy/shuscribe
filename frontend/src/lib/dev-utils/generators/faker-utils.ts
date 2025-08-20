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
      arrayElements: <T>(arr: T[], count?: number) => arr.slice(0, count || 2),
      shuffle: <T>(arr: T[]) => [...arr]
    }
    return faker.helpers
  }
}

// Theme-specific generators with expanded content
export const themeGenerators = {
  fantasy: {
    places: [
      'Stormwind', 'Ironforge', 'Shadowmere', 'Dragonspire', 'Moonhaven', 'Thornwood', 'Silverpeak', 'Ravenshollow',
      'Crystalfall', 'Goldenvale', 'Mistwood', 'Flameheart', 'Starfall', 'Eldergrove', 'Frostholm', 'Sunspear',
      'Blackwater Keep', 'Azure Bay', 'Crimson Peak', 'Whitehaven', 'Shadowbrook', 'Ember Falls'
    ],
    characters: [
      'Elara', 'Theron', 'Lyanna', 'Gareth', 'Seraphina', 'Draven', 'Aria', 'Kael',
      'Aldric', 'Myra', 'Valdris', 'Celyn', 'Mordecai', 'Isadora', 'Tyrion', 'Rhea',
      'Cedric', 'Evangeline', 'Magnus', 'Cordelia', 'Thane', 'Selene', 'Orion', 'Vivienne'
    ],
    titles: [
      'Epic Fantasy', 'The Chronicles of', 'Legends of', 'Tales from', 'The Saga of', 'Adventures in',
      'The Last', 'Rise of the', 'Fall of', 'Quest for', 'Kingdom of', 'Empire of', 'War of the'
    ],
    tags: ['fantasy', 'magic', 'dragons', 'medieval', 'quest', 'adventure', 'epic', 'prophecy', 'kingdoms', 'war'],
    magicSystems: ['Elemental Magic', 'Divine Magic', 'Arcane Arts', 'Blood Magic', 'Rune Magic', 'Spirit Magic'],
    creatures: ['Dragons', 'Griffins', 'Phoenixes', 'Unicorns', 'Shadow Beasts', 'Crystal Golems', 'Storm Eagles'],
    factions: ['Royal Guard', 'Mage Council', 'Dragon Riders', 'Shadow Guild', 'Temple Knights', 'Merchant Alliance'],
    locations: {
      cities: ['Capital', 'Harbor City', 'Trading Post', 'Fortress City', 'Sacred City', 'Border Town'],
      regions: ['Northern Wastes', 'Eastern Kingdoms', 'Western Isles', 'Southern Deserts', 'Central Plains'],
      dungeons: ['Ancient Temple', 'Dragon Lair', 'Abandoned Mine', 'Cursed Tower', 'Underground Ruins']
    },
    folders: {
      characters: ['Characters', 'People', 'Cast', 'Dramatis Personae'],
      locations: ['Locations', 'Places', 'Geography', 'World Atlas', 'Realms'],
      chapters: ['Chapters', 'Story', 'Narrative', 'Book', 'Chronicle'],
      worldBuilding: ['World Building', 'Lore', 'Background', 'Universe', 'Setting'],
      magic: ['Magic System', 'Arcane Arts', 'Mystical Powers', 'Spellcraft'],
      politics: ['Politics', 'Factions', 'Kingdoms', 'Government', 'Alliances']
    }
  },
  scifi: {
    places: [
      'New Terra', 'Quantum Station', 'Nebula Prime', 'Starport Alpha', 'Cybercity', 'Mars Colony', 'Deep Space Nine',
      'Titan Base', 'Europa Outpost', 'Centauri Hub', 'Void Station', 'Nexus Point', 'Binary System',
      'Plasma City', 'Neural Network', 'Hyperdrive Plaza', 'Quantum Lab', 'Asteroid Belt', 'Solar Array'
    ],
    characters: [
      'Zara', 'Rex', 'Nova', 'Cipher', 'Echo', 'Phoenix', 'Vega', 'Orion',
      'Axel', 'Kira', 'Matrix', 'Zenith', 'Flux', 'Nexus', 'Binary', 'Vector',
      'Tesla', 'Darwin', 'Galileo', 'Newton', 'Curie', 'Hawking', 'Sagan', 'Turing'
    ],
    titles: [
      'Space Chronicles', 'Galactic', 'Stellar', 'Cosmic', 'Future', 'Quantum',
      'The Final', 'Beyond the', 'Journey to', 'War for', 'Colony of', 'Empire of the'
    ],
    tags: ['sci-fi', 'space', 'future', 'technology', 'aliens', 'robots', 'cyberpunk', 'AI', 'colony', 'exploration'],
    technologies: ['Faster-Than-Light Travel', 'Artificial Intelligence', 'Quantum Computing', 'Genetic Engineering', 'Cybernetics', 'Terraforming'],
    species: ['Humans', 'Androids', 'Crystalline Beings', 'Energy Entities', 'Hive Minds', 'Silicon-Based Life'],
    factions: ['Federation', 'Colonial Marines', 'Tech Corporations', 'Rebel Alliance', 'AI Collective', 'Trade Consortium'],
    locations: {
      colonies: ['Mining Colony', 'Research Station', 'Trading Hub', 'Military Base', 'Agricultural Dome'],
      ships: ['Battlecruiser', 'Explorer Vessel', 'Transport Ship', 'Science Vessel', 'Stealth Fighter'],
      planets: ['Desert World', 'Ocean Planet', 'Gas Giant', 'Ice World', 'Jungle Planet', 'City Planet']
    },
    folders: {
      characters: ['Characters', 'Personnel', 'Crew', 'Citizens', 'Beings'],
      locations: ['Locations', 'Worlds', 'Colonies', 'Stations', 'Sectors'],
      chapters: ['Chapters', 'Logs', 'Records', 'Chronicles', 'Entries'],
      worldBuilding: ['Universe', 'Galaxy', 'Systems', 'Civilization', 'Technology'],
      tech: ['Technology', 'Science', 'Systems', 'Innovations', 'Discoveries'],
      politics: ['Politics', 'Factions', 'Alliances', 'Governments', 'Corporations']
    }
  },
  mystery: {
    places: [
      'Blackwater', 'Foggy Hollow', 'Old Town', 'The Manor', 'Riverside', 'Millbrook', 'Crescent Bay',
      'Pine Ridge', 'Willow Creek', 'Ashford', 'Maplewood', 'Rosefield', 'Oakenhurst', 'Thornbridge',
      'Stonehaven', 'Clearwater', 'Redwood Heights', 'Silver Lake', 'Golden Valley', 'Cedar Falls'
    ],
    characters: [
      'Detective Morgan', 'Inspector Vale', 'Sarah Chen', 'Marcus Webb', 'Diana Cross', 'Jack Sterling',
      'Agent Rivera', 'Dr. Blackwood', 'Professor Kane', 'Officer Martinez', 'Captain Harris', 'Judge Morrison',
      'Lawyer Thompson', 'Reporter Adams', 'Witness Johnson', 'Suspect Collins', 'Victim Williams', 'Expert Davis'
    ],
    titles: [
      'Mystery of', 'The Case of', 'Murder at', 'Secrets of', 'The Disappearance of', 'Death in',
      'Last Seen in', 'The Truth About', 'Hidden in', 'Blood on', 'Shadows over', 'The Final'
    ],
    tags: ['mystery', 'crime', 'detective', 'thriller', 'investigation', 'murder', 'suspense', 'clues', 'forensics', 'police'],
    crimeTypes: ['Murder', 'Theft', 'Kidnapping', 'Fraud', 'Arson', 'Blackmail', 'Embezzlement', 'Missing Person'],
    evidence: ['Fingerprints', 'DNA Evidence', 'Witness Testimony', 'Security Footage', 'Phone Records', 'Financial Records'],
    locations: {
      scenes: ['Crime Scene', 'Police Station', 'Courthouse', 'Hospital', 'Hotel', 'Restaurant', 'Office Building'],
      areas: ['Downtown', 'Suburbs', 'Industrial District', 'Waterfront', 'Historic Quarter', 'Business District'],
      buildings: ['Mansion', 'Apartment', 'Warehouse', 'Factory', 'Library', 'Museum', 'School']
    },
    folders: {
      characters: ['Characters', 'People', 'Suspects', 'Witnesses', 'Investigators'],
      locations: ['Locations', 'Scenes', 'Places', 'Areas', 'Settings'],
      chapters: ['Chapters', 'Case Files', 'Timeline', 'Events', 'Investigation'],
      evidence: ['Evidence', 'Clues', 'Facts', 'Leads', 'Findings'],
      notes: ['Notes', 'Research', 'Background', 'Records', 'Files']
    }
  },
  modern: {
    places: [
      'Metro City', 'Downtown', 'University Campus', 'Corporate Plaza', 'Shopping Center', 'Residential Area',
      'Tech Hub', 'Arts District', 'Financial District', 'Medical Center', 'Airport', 'Waterfront',
      'Innovation Park', 'Green Valley', 'Sunset Boulevard', 'Harbor View', 'Central Station', 'Business Bay'
    ],
    characters: [
      'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn',
      'Dr. Smith', 'Professor Johnson', 'CEO Williams', 'Director Brown', 'Manager Davis', 'Engineer Lee',
      'Artist Garcia', 'Writer Anderson', 'Student Wilson', 'Entrepreneur Martinez', 'Consultant Rodriguez'
    ],
    titles: [
      'Modern Life', 'City Stories', 'Urban Tales', 'Contemporary', 'Today\'s World', 'Current Affairs',
      'Life in', 'Stories from', 'Chronicles of', 'Voices from', 'Scenes from'
    ],
    tags: ['modern', 'contemporary', 'urban', 'realistic', 'drama', 'relationship', 'career', 'family', 'technology', 'society'],
    themes: ['Technology Impact', 'Social Media', 'Work-Life Balance', 'Environmental Issues', 'Mental Health', 'Relationships'],
    settings: ['Office', 'University', 'Hospital', 'Tech Company', 'Art Gallery', 'Coffee Shop', 'Startup'],
    folders: {
      characters: ['Characters', 'People', 'Protagonists', 'Cast'],
      locations: ['Locations', 'Settings', 'Places', 'Venues'],
      chapters: ['Chapters', 'Stories', 'Episodes', 'Scenes'],
      research: ['Research', 'Background', 'References', 'Sources'],
      themes: ['Themes', 'Topics', 'Issues', 'Concepts']
    }
  }
}

// Get random theme
export const getRandomTheme = async (): Promise<keyof typeof themeGenerators> => {
  const helpers = await safeFaker.helpers()
  const themes = Object.keys(themeGenerators) as Array<keyof typeof themeGenerators>
  return helpers.arrayElement(themes) || 'fantasy'
}

// Helper functions for dynamic content generation
export const generateThemeContent = {
  // Generate varied project title
  async projectTitle(theme: keyof typeof themeGenerators): Promise<string> {
    const helpers = await safeFaker.helpers()
    const themeData = themeGenerators[theme]
    const titlePrefix = helpers.arrayElement(themeData.titles) || 'The Story of'
    const placeName = helpers.arrayElement(themeData.places) || 'Unknown Place'
    return `${titlePrefix} ${placeName}`
  },

  // Generate character name with theme
  async characterName(theme: keyof typeof themeGenerators): Promise<string> {
    const helpers = await safeFaker.helpers()
    const person = await safeFaker.person()
    const themeData = themeGenerators[theme]
    
    if (theme === 'modern') {
      return `${helpers.arrayElement(themeData.characters) || 'Character'} ${await person.lastName()}`
    } else {
      return helpers.arrayElement(themeData.characters) || 'Character'
    }
  },

  // Generate location name with theme
  async locationName(theme: keyof typeof themeGenerators): Promise<string> {
    const helpers = await safeFaker.helpers()
    const themeData = themeGenerators[theme]
    return helpers.arrayElement(themeData.places) || 'Unknown Location'
  },

  // Generate chapter title with theme
  async chapterTitle(theme: keyof typeof themeGenerators, chapterNumber: number): Promise<string> {
    const helpers = await safeFaker.helpers()
    const themeData = themeGenerators[theme]
    
    const chapterTitles = theme === 'fantasy' 
      ? ['The Awakening', 'Quest Begins', 'Dark Forest', 'Dragon\'s Lair', 'Magic Revealed', 'Battle of Storms', 'Ancient Secrets', 'The Prophecy', 'Final Stand']
      : theme === 'scifi' 
      ? ['First Contact', 'The Discovery', 'Quantum Leap', 'AI Uprising', 'Deep Space', 'Final Protocol', 'System Failure', 'New Worlds', 'Evolution']
      : theme === 'mystery'
      ? ['The Crime', 'First Clues', 'The Investigation', 'Hidden Motives', 'The Chase', 'Truth Revealed', 'Final Evidence', 'Justice Served']
      : ['The Beginning', 'New Challenges', 'Turning Point', 'Complications', 'Resolution', 'New Direction', 'Full Circle', 'The End']

    const title = helpers.arrayElement(chapterTitles) || 'The Beginning'
    return `Chapter ${chapterNumber}: ${title}`
  },

  // Generate folder name variations
  async folderName(theme: keyof typeof themeGenerators, folderType: string): Promise<string> {
    const helpers = await safeFaker.helpers()
    const themeData = themeGenerators[theme]
    const folderOptions = (themeData.folders as any)[folderType] || ['Folder']
    return helpers.arrayElement(folderOptions) || 'Folder'
  },

  // Generate document type and content hints
  async documentType(theme: keyof typeof themeGenerators): Promise<{type: string, icon: string, tags: string[]}> {
    const helpers = await safeFaker.helpers()
    const number = await safeFaker.number()
    
    const documentTypes = [
      { type: 'character', icon: 'User', tags: ['character', 'person'] },
      { type: 'location', icon: 'MapPin', tags: ['location', 'place'] },
      { type: 'chapter', icon: 'BookOpen', tags: ['chapter', 'story'] },
      { type: 'worldbuilding', icon: 'Globe', tags: ['worldbuilding', 'lore'] },
      { type: 'research', icon: 'Search', tags: ['research', 'notes'] },
      { type: 'timeline', icon: 'Clock', tags: ['timeline', 'events'] },
      { type: 'relationships', icon: 'Heart', tags: ['relationships', 'connections'] },
      { type: 'outline', icon: 'List', tags: ['outline', 'structure'] }
    ]
    
    const selected = helpers.arrayElement(documentTypes) || { type: 'document', icon: 'File', tags: ['document'] }
    return {
      ...selected,
      tags: [...selected.tags, theme, ...(await this.getThemeSpecificTags(theme))]
    }
  },

  // Get theme-specific tags
  async getThemeSpecificTags(theme: keyof typeof themeGenerators): Promise<string[]> {
    const helpers = await safeFaker.helpers()
    const number = await safeFaker.number()
    const themeData = themeGenerators[theme]
    const numTags = await number.int({ min: 1, max: 3 })
    return helpers.arrayElements(themeData.tags, numTags)
  }
}