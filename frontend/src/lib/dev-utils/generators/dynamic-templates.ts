/**
 * Dynamic Template Generator - Faker-powered markdown content creation
 * 
 * WHY: Creates varied, realistic markdown content for seeding instead of static templates.
 * Uses faker.js to generate different content each time while maintaining quality
 * and showcasing TipTap editor capabilities with rich formatting.
 * 
 * Each function returns markdown strings that are converted to ProseMirror JSON
 * using the markdownToTipTap helper for proper editor display.
 */

import { safeFaker, themeGenerators, generateThemeContent } from './faker-utils'

// Helper function to safely join words array or return string as-is
const safeJoinWords = (wordsResult: string | string[]): string => {
  return Array.isArray(wordsResult) ? wordsResult.join(' ') : wordsResult
}

// Generate dynamic character template with theme variations
export async function generateCharacterTemplate(theme: keyof typeof themeGenerators): Promise<string> {
  const person = await safeFaker.person()
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const characterName = await generateThemeContent.characterName(theme)
  const themeData = themeGenerators[theme]
  
  // Theme-specific content
  const abilities = theme === 'fantasy' 
    ? helpers.arrayElements(['Fire Magic', 'Healing', 'Swordsmanship', 'Beast Taming', 'Elemental Control', 'Prophecy', 'Stealth', 'Leadership'], 3)
    : theme === 'scifi' 
    ? helpers.arrayElements(['Cybernetic Enhancement', 'Quantum Computing', 'Zero-G Navigation', 'AI Interfacing', 'Energy Manipulation', 'Teleportation', 'Mind Reading'], 3)
    : theme === 'mystery'
    ? helpers.arrayElements(['Investigation', 'Deductive Reasoning', 'Forensic Analysis', 'Interrogation', 'Surveillance', 'Criminal Psychology'], 3)
    : helpers.arrayElements(['Leadership', 'Communication', 'Problem Solving', 'Technical Skills', 'Creative Thinking'], 3)

  const relationships = [
    { name: await generateThemeContent.characterName(theme), relation: 'Ally', status: 'Active' },
    { name: await generateThemeContent.characterName(theme), relation: 'Rival', status: 'Complicated' },
    { name: await generateThemeContent.characterName(theme), relation: 'Mentor', status: 'Missing' }
  ]

  const age = await number.int({ min: 18, max: 65 })
  const occupation = theme === 'fantasy' 
    ? helpers.arrayElement(['Mage', 'Knight', 'Scholar', 'Merchant', 'Healer', 'Ranger', 'Noble'])
    : theme === 'scifi'
    ? helpers.arrayElement(['Engineer', 'Pilot', 'Scientist', 'Doctor', 'Commander', 'Trader', 'Explorer'])
    : theme === 'mystery'
    ? helpers.arrayElement(['Detective', 'Forensic Expert', 'Lawyer', 'Journalist', 'Professor', 'Consultant'])
    : helpers.arrayElement(['Manager', 'Designer', 'Developer', 'Teacher', 'Entrepreneur', 'Artist'])

  // Pre-resolve async values for template
  const backgroundPara1 = await lorem.paragraph()
  const backgroundPara2 = await lorem.paragraph()
  const conflict1Type = helpers.arrayElement(['Identity Crisis', 'Moral Dilemma', 'Past Trauma', 'Fear of Failure', 'Trust Issues'])
  const conflict1Desc = await lorem.sentence()
  const conflict2Type = helpers.arrayElement(['Self Doubt', 'Responsibility Burden', 'Relationship Struggles', 'Power Corruption', 'Loss of Purpose'])
  const conflict2Desc = await lorem.sentence()
  const shortTermGoal = await lorem.sentence()
  const longTermGoal = await lorem.sentence()
  const hiddenGoal = await lorem.sentence()
  const quote = await lorem.sentence()
  const notes = await lorem.sentence()

  return `# ${characterName}

## Character Profile

**Age**: ${age} years  
**Occupation**: ${occupation}  
**Key Traits**: ${helpers.arrayElements(['Determined', 'Curious', 'Brave', 'Cautious', 'Charismatic', 'Analytical', 'Creative', 'Loyal'], 3).join(', ')}

## Background

${backgroundPara1}

${backgroundPara2}

## Abilities & Skills

### Primary Skills
${abilities.map(ability => `- [x] **${ability}** - Specialized skill in this area`).join('\n')}
- [ ] **Advanced Training** - Skill development in progress

### Equipment & Resources
${theme === 'fantasy' 
  ? `- **Weapon**: ${helpers.arrayElement(['Enchanted Sword', 'Magic Staff', 'Ancient Bow', 'Crystal Dagger', 'War Hammer'])}\n- **Armor**: ${helpers.arrayElement(['Leather Armor', 'Chain Mail', 'Robes of Power', 'Plate Armor', 'Magical Cloak'])}`
  : theme === 'scifi'
  ? `- **Equipment**: ${helpers.arrayElement(['Plasma Rifle', 'Neural Interface', 'Quantum Scanner', 'Gravity Suit', 'AI Assistant'])}\n- **Vehicle**: ${helpers.arrayElement(['Starfighter', 'Hover Bike', 'Transport Pod', 'Mech Suit', 'Research Vessel'])}`
  : theme === 'mystery'
  ? `- **Tools**: ${helpers.arrayElement(['Forensic Kit', 'Digital Scanner', 'Investigation Badge', 'Surveillance Gear', 'Database Access'])}\n- **Resources**: ${helpers.arrayElement(['Police Network', 'Expert Contacts', 'Case Files', 'Lab Access', 'Legal Authority'])}`
  : `- **Resources**: ${helpers.arrayElement(['Professional Network', 'Technical Equipment', 'Research Access', 'Communication Tools', 'Project Management'])}\n- **Skills**: ${helpers.arrayElement(['Industry Knowledge', 'Team Leadership', 'Strategic Planning', 'Problem Solving', 'Innovation'])}`
}

## Character Development

### Internal Conflicts
- **${conflict1Type}**: ${conflict1Desc}
- **${conflict2Type}**: ${conflict2Desc}

### Goals & Motivations
1. **Short-term**: ${shortTermGoal}
2. **Long-term**: ${longTermGoal}  
3. **Hidden**: ${hiddenGoal}

## Relationships

| Character | Relationship | Status | Notes |
|-----------|--------------|--------|-------|
${relationships.map(rel => `| **${rel.name}** | ${rel.relation} | ${rel.status} | Character notes |`).join('\n')}

## Character Arc

### Act 1: Introduction
Character introduction and initial setup.

### Act 2: Development  
Character growth and conflict development.

### Act 3: Resolution
Character transformation and story conclusion.

---

> *"${quote}"*
> 
> — **${characterName}**, ${theme === 'fantasy' ? 'speaking to the Council' : theme === 'scifi' ? 'final mission log' : theme === 'mystery' ? 'closing statement' : 'team meeting'}

**Character Created**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Notes**: ${notes}`
}

// Generate dynamic location template with theme variations
export async function generateLocationTemplate(theme: keyof typeof themeGenerators): Promise<string> {
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const locationName = await generateThemeContent.locationName(theme)
  const themeData = themeGenerators[theme]
  
  const population = await number.int({ min: 100, max: 100000 })
  const features = theme === 'fantasy' 
    ? helpers.arrayElements(['Ancient Ruins', 'Mystical Forest', 'Crystal Caves', 'Dragon Lair', 'Magical Springs', 'Enchanted Grove', 'Sacred Temple'], 4)
    : theme === 'scifi' 
    ? helpers.arrayElements(['Orbital Platform', 'Quantum Laboratory', 'Terraforming Station', 'Hyperspace Gate', 'AI Core', 'Energy Reactor', 'Research Facility'], 4)
    : theme === 'mystery'
    ? helpers.arrayElements(['Historic District', 'Waterfront', 'University Campus', 'Industrial Zone', 'Government Buildings', 'Cultural Center'], 4)
    : helpers.arrayElements(['Business District', 'Residential Area', 'Entertainment Zone', 'Shopping Center', 'Cultural Quarter', 'Tech Hub'], 4)

  return `# ${locationName}

## Location Overview

**Type**: ${theme === 'fantasy' ? helpers.arrayElement(['City', 'Village', 'Fortress', 'Kingdom', 'Sacred Site']) : theme === 'scifi' ? helpers.arrayElement(['Colony', 'Station', 'Planet', 'Outpost', 'Sector']) : theme === 'mystery' ? helpers.arrayElement(['City', 'Town', 'Neighborhood', 'District', 'Complex']) : helpers.arrayElement(['City', 'Campus', 'Complex', 'District', 'Center'])}  
**Population**: ${population.toLocaleString()}  
**Climate**: ${helpers.arrayElement(['Temperate', 'Tropical', 'Arid', 'Cold', 'Variable', 'Controlled'])}  
**Status**: ${helpers.arrayElement(['Thriving', 'Declining', 'Growing', 'Stable', 'Changing', 'Rebuilding'])}

## Description

${await lorem.paragraph()}

${await lorem.paragraph()}

---

## Notable Features

### Primary Locations
${features.map(feature => `- **${feature}**: Notable location feature`).join('\n')}

### Points of Interest

| Location | Type | Significance | Access |
|----------|------|--------------|--------|
${await Promise.all(Array.from({length: 3}, async () => {
  const name = theme === 'fantasy' 
    ? helpers.arrayElement(['The Golden Hall', 'Shadow Market', 'Temple of Light', 'Mystic Library', 'Crystal Tower'])
    : theme === 'scifi'
    ? helpers.arrayElement(['Command Center', 'Research Lab', 'Docking Bay', 'Energy Core', 'Communications Hub'])
    : theme === 'mystery'
    ? helpers.arrayElement(['Police Station', 'City Hall', 'Museum', 'Library', 'Court House'])
    : helpers.arrayElement(['Main Office', 'Conference Center', 'Innovation Lab', 'Community Space', 'Resource Center'])
  
  return `| **${name}** | ${helpers.arrayElement(['Public', 'Restricted', 'Private', 'Special'])} | ${helpers.arrayElement(['High', 'Medium', 'Low', 'Secret'])} | ${helpers.arrayElement(['Open', 'Limited', 'Invitation', 'Authorized'])} |`
})).then(rows => rows.join('\n'))}

## Demographics & Culture

### Population Breakdown
${theme === 'fantasy' 
  ? `- **Humans**: ${await number.int({ min: 40, max: 80 })}%
- **Elves**: ${await number.int({ min: 10, max: 30 })}%
- **Dwarves**: ${await number.int({ min: 5, max: 20 })}%
- **Others**: ${await number.int({ min: 5, max: 15 })}%`
  : theme === 'scifi'
  ? `- **Humans**: ${await number.int({ min: 30, max: 70 })}%
- **Androids**: ${await number.int({ min: 10, max: 30 })}%
- **Alien Species**: ${await number.int({ min: 10, max: 40 })}%
- **AI Entities**: ${await number.int({ min: 5, max: 15 })}%`
  : `- **Residents**: ${await number.int({ min: 60, max: 85 })}%
- **Workers**: ${await number.int({ min: 10, max: 25 })}%
- **Visitors**: ${await number.int({ min: 5, max: 15 })}%`
}

### Cultural Elements
- **${helpers.arrayElement(['Primary Language', 'Common Tongue', 'Official Language'])}**: ${helpers.arrayElement(['Standard', 'Local Dialect', 'Trade Language', 'Ancient Script'])}
- **${helpers.arrayElement(['Main Religion', 'Belief System', 'Philosophy'])}**: Local beliefs and practices
- **${helpers.arrayElement(['Traditions', 'Customs', 'Festivals'])}**: Cultural traditions and celebrations

## Government & Politics

### Leadership Structure
${theme === 'fantasy' 
  ? `**Ruler**: ${helpers.arrayElement(['King/Queen', 'Lord/Lady', 'Council Elder', 'High Mage', 'Chosen Leader'])}  
**Government**: ${helpers.arrayElement(['Monarchy', 'Council Rule', 'Theocracy', 'Magocracy', 'Federation'])}`
  : theme === 'scifi'
  ? `**Leadership**: ${helpers.arrayElement(['Administrator', 'Commander', 'AI Governor', 'Elected Council', 'Corporate Board'])}  
**System**: ${helpers.arrayElement(['Democratic', 'Corporate', 'Military', 'AI-Managed', 'Colonial'])}`
  : `**Leadership**: ${helpers.arrayElement(['Mayor', 'Director', 'Council', 'Board', 'Commissioner'])}  
**System**: ${helpers.arrayElement(['Democratic', 'Administrative', 'Corporate', 'Academic', 'Cooperative'])}`
}

### Current Issues
- [x] **${helpers.arrayElement(['Resource Management', 'Security Concerns', 'Growth Planning', 'Environmental Issues', 'Political Tensions'])}** - Currently being addressed
- [x] **${helpers.arrayElement(['Economic Development', 'Infrastructure', 'Population Growth', 'Cultural Preservation', 'Technology Integration'])}** - Ongoing project
- [ ] **${helpers.arrayElement(['Expansion Plans', 'Diplomatic Relations', 'Research Initiatives', 'Defense Upgrades', 'Social Programs'])}** - Future consideration

## Points of Interest for Visitors

### Must-See Locations
1. **${features[0]}** - ${await lorem.sentence()}
2. **${features[1]}** - ${await lorem.sentence()}
3. **${features[2]}** - ${await lorem.sentence()}

### Local Specialties
${theme === 'fantasy' 
  ? `- **Crafts**: ${helpers.arrayElements(['Enchanted Items', 'Magical Potions', 'Blessed Weapons', 'Crystal Jewelry', 'Ancient Scrolls'], 2).join(', ')}
- **Food**: ${helpers.arrayElements(['Dragon Steak', 'Elven Bread', 'Dwarven Ale', 'Healing Herbs', 'Magical Fruits'], 2).join(', ')}`
  : theme === 'scifi'
  ? `- **Technology**: ${helpers.arrayElements(['Quantum Devices', 'Neural Implants', 'Energy Weapons', 'AI Assistants', 'Nano-materials'], 2).join(', ')}
- **Services**: ${helpers.arrayElements(['Genetic Therapy', 'Memory Enhancement', 'Cybernetic Repair', 'Quantum Transport', 'AI Consulting'], 2).join(', ')}`
  : `- **Services**: ${helpers.arrayElements(['Expert Consultation', 'Investigation Support', 'Research Access', 'Training Programs', 'Equipment Rental'], 2).join(', ')}
- **Amenities**: ${helpers.arrayElements(['Conference Facilities', 'Dining Options', 'Entertainment', 'Accommodation', 'Transportation'], 2).join(', ')}`
}

---

## Adventure Hooks

### Current Events
Recent events and activities in the area provide opportunities for interaction and adventure.

### Opportunities
- **Economic Development**: Business and trade opportunities
- **Cultural Exchange**: Learning and cultural opportunities  
- **Adventure Possibilities**: Exploration and discovery opportunities

> *"This location offers many possibilities for travelers and adventurers."*
> 
> — **Local ${theme === 'fantasy' ? 'Guide' : theme === 'scifi' ? 'Administrator' : 'Official'}**

**Location Created**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Travel Notes**: Important location for story development`
}

// Generate dynamic chapter template with theme variations
export async function generateChapterTemplate(theme: keyof typeof themeGenerators, chapterNumber: number): Promise<string> {
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const chapterTitle = await generateThemeContent.chapterTitle(theme, chapterNumber)
  
  const protagonist = await generateThemeContent.characterName(theme)
  const location = await generateThemeContent.locationName(theme)
  
  const wordCount = await number.int({ min: 800, max: 2500 })

  return `# ${chapterTitle}

${await lorem.paragraph()}

${await lorem.paragraph()}

---

## Scene: ${helpers.arrayElement(['Opening', 'Confrontation', 'Discovery', 'Revelation', 'Action', 'Dialogue', 'Reflection'])}

### Setting
**Location**: ${location}  
**Time**: ${helpers.arrayElement(['Dawn', 'Morning', 'Midday', 'Afternoon', 'Evening', 'Night', 'Midnight'])}  
**Weather**: ${helpers.arrayElement(['Clear', 'Stormy', 'Foggy', 'Rainy', 'Windy', 'Calm'])}

${await lorem.paragraph()}

### Character Focus: ${protagonist}

${await lorem.paragraph()}

> *"${await lorem.sentence()}"*

${await lorem.paragraph()}

---

## Key Events

### Event 1: ${helpers.arrayElement(['The Discovery', 'The Confrontation', 'The Challenge', 'The Revelation', 'The Decision'])}

${await lorem.paragraph()}

**Consequences**: ${await lorem.sentence()}

### Event 2: ${helpers.arrayElement(['Character Development', 'Plot Advancement', 'Conflict Resolution', 'New Mystery', 'Relationship Change'])}

${await lorem.paragraph()}

| Character | Action | Motivation | Outcome |
|-----------|--------|------------|---------|
| **${protagonist}** | ${helpers.arrayElement(['Investigates', 'Confronts', 'Discovers', 'Decides', 'Protects'])} | Character motivation | ${helpers.arrayElement(['Success', 'Partial Success', 'Complication', 'Failure', 'Unexpected'])} |
| **Supporting Character** | ${helpers.arrayElement(['Supports', 'Opposes', 'Questions', 'Reveals', 'Escapes'])} | Personal reasons | ${helpers.arrayElement(['Helpful', 'Harmful', 'Neutral', 'Surprising', 'Unclear'])} |

---

## Dialogue & Character Interaction

### Key Conversation
${await lorem.paragraph()}

**${protagonist}**: "${await lorem.sentence()}"

**${await generateThemeContent.characterName(theme)}**: "${await lorem.sentence()}"

${await lorem.paragraph()}

---

## Chapter Resolution

### Immediate Outcomes
- [x] **${helpers.arrayElement(['Conflict resolved', 'Mystery deepened', 'Character developed', 'Plot advanced', 'Tension increased'])}**
- [x] **${helpers.arrayElement(['New information revealed', 'Relationship changed', 'Goal achieved', 'Obstacle overcome', 'Alliance formed'])}**
- [ ] **${helpers.arrayElement(['Future challenge hinted', 'Unresolved tension', 'Mystery element', 'Character growth needed', 'Plot thread'])}**

### Cliffhanger Setup
${await lorem.paragraph()}

### Chapter Impact
**Character Development**: ${await lorem.sentence()}  
**Plot Advancement**: ${await lorem.sentence()}  
**Theme Exploration**: ${await lorem.sentence()}

---

**To be continued in Chapter ${chapterNumber + 1}...**

---

**Chapter Stats:**
- **Word Count**: ~${wordCount} words
- **POV Character**: ${protagonist}
- **Setting**: ${location}
- **Theme**: ${helpers.arrayElement(['Courage', 'Discovery', 'Sacrifice', 'Growth', 'Truth', 'Justice', 'Love', 'Redemption'])}
- **Tone**: ${helpers.arrayElement(['Suspenseful', 'Hopeful', 'Dark', 'Uplifting', 'Mysterious', 'Action-packed', 'Emotional', 'Contemplative'])}

**Created**: ${(await date.past()).toLocaleDateString()}  
**Revised**: ${new Date().toLocaleDateString()}`
}

// Generate dynamic world-building template
export async function generateWorldBuildingTemplate(theme: keyof typeof themeGenerators, documentType: string): Promise<string> {
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const number = await safeFaker.number()
  const date = await safeFaker.date()

  const themeData = themeGenerators[theme]
  
  if (documentType === 'magic' && theme === 'fantasy') {
    const magicSystems = 'magicSystems' in themeData ? themeData.magicSystems : ['Magic System']
    const magicSystem = helpers.arrayElement(magicSystems || ['Magic System']) || 'Magic System'
    
    // Pre-resolve word combinations
    const principleWords = safeJoinWords(await lorem.words(3))
    
    return `# ${magicSystem}

## Overview

${await lorem.paragraph()}

The ${magicSystem.toLowerCase()} operates on the principle of ${principleWords}, where practitioners must ${await lorem.sentence()}

---

## How Magic Works

### Core Principles
1. **${helpers.arrayElement(['Source', 'Channel', 'Focus', 'Control', 'Balance'])}**: ${await lorem.sentence()}
2. **${helpers.arrayElement(['Limitation', 'Cost', 'Risk', 'Requirement', 'Restriction'])}**: ${await lorem.sentence()}
3. **${helpers.arrayElement(['Training', 'Mastery', 'Development', 'Growth', 'Evolution'])}**: ${await lorem.sentence()}

### Power Levels

| Level | Name | Abilities | Training Time |
|-------|------|-----------|---------------|
| 1 | **${helpers.arrayElement(['Novice', 'Initiate', 'Student', 'Apprentice'])}** | Basic ${magicSystem.split(' ')[0].toLowerCase()} manipulation | ${await number.int({ min: 1, max: 3 })} years |
| 2 | **${helpers.arrayElement(['Adept', 'Practitioner', 'Journeyman', 'Scholar'])}** | Intermediate spells and techniques | ${await number.int({ min: 5, max: 10 })} years |
| 3 | **${helpers.arrayElement(['Expert', 'Master', 'Sage', 'Archmage'])}** | Advanced mastery and teaching | ${await number.int({ min: 15, max: 25 })} years |

---

## Magical Abilities

### Primary Schools
${helpers.arrayElements(['Offensive Magic', 'Defensive Magic', 'Healing Magic', 'Illusion Magic', 'Divination Magic', 'Transmutation Magic'], 3).map(school => 
  `- **${school}**: ${lorem.sentence()}`
).join('\n')}

### Spell Examples
\`\`\`
${helpers.arrayElement(['Flame Burst', 'Healing Light', 'Shield Wall', 'Mind Read', 'Transform'])}
Components: ${helpers.arrayElement(['Verbal + Somatic', 'Material Focus', 'Mental Concentration', 'Emotional State'])}
Duration: ${helpers.arrayElement(['Instant', '1 minute', '10 minutes', '1 hour', 'Permanent'])}
Range: ${helpers.arrayElement(['Touch', '30 feet', '100 feet', 'Line of sight', 'Unlimited'])}
\`\`\`

---

## Cultural Impact

### Social Structure
Magic users in society are typically:
- **${helpers.arrayElement(['Revered', 'Feared', 'Regulated', 'Hidden', 'Integrated'])}** by the general population
- **${helpers.arrayElement(['Organized', 'Independent', 'Monitored', 'Trained', 'Licensed'])}** through formal institutions
- **${helpers.arrayElement(['Wealthy', 'Diverse', 'Elite', 'Common', 'Outcast'])}** in terms of social status

### Magic in Daily Life
${await lorem.paragraph()}

---

## Limitations & Costs

### Physical Limitations
- [x] **Energy Drain**: ${await lorem.sentence()}
- [x] **Material Components**: ${await lorem.sentence()}
- [ ] **Environmental Factors**: ${await lorem.sentence()}

### Magical Restrictions
- **${helpers.arrayElement(['Ethical Codes', 'Legal Restrictions', 'Religious Taboos', 'Cultural Norms'])}**: ${await lorem.sentence()}
- **${helpers.arrayElement(['Power Limits', 'Skill Requirements', 'Training Needs', 'Natural Barriers'])}**: ${await lorem.sentence()}

---

**System Created**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Notes**: ${await lorem.sentence()}`
  } else if (documentType === 'technology' && theme === 'scifi') {
    const technologies = 'technologies' in themeData ? themeData.technologies : ['Advanced Technology']
    const technology = helpers.arrayElement(technologies || ['Advanced Technology']) || 'Advanced Technology'
    
    // Pre-resolve word combinations
    const breakthroughWords = safeJoinWords(await lorem.words(2))
    
    return `# ${technology}

## Technology Overview

${await lorem.paragraph()}

The ${technology.toLowerCase()} represents a breakthrough in ${breakthroughWords}, enabling ${await lorem.sentence()}

---

## Technical Specifications

### Core Components
1. **${helpers.arrayElement(['Processor', 'Engine', 'Core', 'Matrix', 'Network'])}**: ${await lorem.sentence()}
2. **${helpers.arrayElement(['Interface', 'Controller', 'Regulator', 'Monitor', 'Optimizer'])}**: ${await lorem.sentence()}
3. **${helpers.arrayElement(['Power Source', 'Energy Cell', 'Reactor', 'Generator', 'Battery'])}**: ${await lorem.sentence()}

### Performance Metrics

| Attribute | Specification | Standard | Maximum |
|-----------|---------------|----------|---------|
| **Processing Speed** | ${await number.int({ min: 10, max: 1000 })} THz | Industry baseline | ${await number.int({ min: 1000, max: 5000 })} THz |
| **Energy Efficiency** | ${await number.int({ min: 85, max: 99 })}% | Energy conservation | 99.9% theoretical |
| **Range/Capacity** | ${await number.int({ min: 1, max: 100 })} km | Operational limit | ${await number.int({ min: 500, max: 10000 })} km |

---

## Applications & Uses

### Primary Functions
${helpers.arrayElements(['Communication', 'Transportation', 'Research', 'Defense', 'Manufacturing', 'Medical'], 3).map(func => 
  `- **${func}**: ${lorem.sentence()}`
).join('\n')}

### Implementation Examples
\`\`\`
System Configuration:
- Hardware: ${helpers.arrayElement(['Quantum Processor', 'Neural Network', 'Plasma Core', 'Fusion Reactor'])}
- Software: ${helpers.arrayElement(['AI Controller', 'Adaptive Algorithm', 'Learning Protocol', 'Smart Interface'])}
- Interface: ${helpers.arrayElement(['Neural Link', 'Holographic Display', 'Voice Command', 'Gesture Control'])}
\`\`\`

---

## Societal Impact

### Economic Effects
${await lorem.paragraph()}

### Cultural Changes
The introduction of ${technology.toLowerCase()} has:
- **${helpers.arrayElement(['Revolutionized', 'Transformed', 'Enhanced', 'Disrupted', 'Improved'])}** daily life
- **${helpers.arrayElement(['Created', 'Eliminated', 'Modified', 'Expanded', 'Limited'])}** job opportunities
- **${helpers.arrayElement(['Increased', 'Decreased', 'Changed', 'Stabilized', 'Complicated'])}** social interactions

---

## Limitations & Risks

### Technical Constraints
- [x] **${helpers.arrayElement(['Power Requirements', 'Processing Limits', 'Material Costs', 'Complexity Issues'])}**: ${await lorem.sentence()}
- [x] **${helpers.arrayElement(['Compatibility', 'Scalability', 'Reliability', 'Security'])}**: ${await lorem.sentence()}
- [ ] **${helpers.arrayElement(['Future Upgrades', 'System Integration', 'User Training', 'Maintenance'])}**: ${await lorem.sentence()}

### Safety Considerations
- **${helpers.arrayElement(['Radiation Exposure', 'System Failure', 'User Error', 'Malfunction Risk'])}**: ${await lorem.sentence()}
- **${helpers.arrayElement(['Security Breach', 'Data Loss', 'Privacy Concerns', 'Unauthorized Access'])}**: ${await lorem.sentence()}

---

**Technology Developed**: ${(await date.past()).toLocaleDateString()}  
**Current Version**: ${await number.float({ min: 1.0, max: 5.0, fractionDigits: 1 })}  
**Next Update**: ${(await date.recent()).toLocaleDateString()}  
**Research Notes**: ${await lorem.sentence()}`
  }
  
  // Generic research/notes template
  // Pre-resolve word combinations
  const explorationWords = safeJoinWords(await lorem.words(3))
  
  return `# ${documentType.charAt(0).toUpperCase() + documentType.slice(1)} Research

## Research Overview

${await lorem.paragraph()}

This document explores ${explorationWords} in the context of ${theme} storytelling.

---

## Key Findings

### Primary Research
${await lorem.paragraph()}

### Secondary Sources
1. **${safeJoinWords(await lorem.words(2))}**: ${await lorem.sentence()}
2. **${safeJoinWords(await lorem.words(2))}**: ${await lorem.sentence()}
3. **${safeJoinWords(await lorem.words(2))}**: ${await lorem.sentence()}

---

## Notes & Observations

### Important Points
- [x] **${safeJoinWords(await lorem.words(3))}** - Verified information
- [x] **${safeJoinWords(await lorem.words(3))}** - Confirmed details
- [ ] **${safeJoinWords(await lorem.words(3))}** - Requires further research

### Questions for Further Investigation
1. ${await lorem.sentence()}
2. ${await lorem.sentence()}
3. ${await lorem.sentence()}

---

**Research Date**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Status**: ${helpers.arrayElement(['In Progress', 'Complete', 'Needs Review', 'Preliminary'])}`
}

// Generate research/notes template
export async function generateResearchTemplate(theme: keyof typeof themeGenerators): Promise<string> {
  const lorem = await safeFaker.lorem()
  const helpers = await safeFaker.helpers()
  const date = await safeFaker.date()

  const researchTopic = theme === 'fantasy' 
    ? helpers.arrayElement(['Ancient Civilizations', 'Medieval Warfare', 'Mythology Research', 'Historical Magic', 'Castle Architecture'])
    : theme === 'scifi'
    ? helpers.arrayElement(['Quantum Physics', 'Space Exploration', 'AI Development', 'Genetic Engineering', 'Future Technology'])
    : theme === 'mystery'
    ? helpers.arrayElement(['Forensic Science', 'Criminal Psychology', 'Investigation Methods', 'Legal Procedures', 'Case Studies'])
    : helpers.arrayElement(['Social Trends', 'Technology Impact', 'Cultural Studies', 'Psychological Research', 'Behavior Analysis'])

  return `# ${researchTopic} Research

## Research Objective

${await lorem.paragraph()}

The goal of this research is to ${await lorem.sentence()}

---

## Sources & References

### Primary Sources
1. **${safeJoinWords(await lorem.words(3))}** - ${await lorem.sentence()}
2. **${safeJoinWords(await lorem.words(3))}** - ${await lorem.sentence()}
3. **${safeJoinWords(await lorem.words(3))}** - ${await lorem.sentence()}

### Secondary Sources
- **Books**: ${safeJoinWords(await lorem.words(4))}
- **Articles**: ${safeJoinWords(await lorem.words(4))}
- **Interviews**: ${safeJoinWords(await lorem.words(3))}

---

## Key Findings

### Important Facts
${helpers.arrayElements(['Historical Context', 'Technical Details', 'Cultural Significance', 'Modern Applications', 'Future Implications'], 3).map(async finding => 
  `- **${finding}**: ${await lorem.sentence()}`
).join('\n')}

### Research Notes
${await lorem.paragraph()}

${await lorem.paragraph()}

---

## Application to Story

### How This Research Helps
${await lorem.paragraph()}

### Story Elements Influenced
- [x] **Character Development**: ${await lorem.sentence()}
- [x] **Plot Details**: ${await lorem.sentence()}
- [x] **World Building**: ${await lorem.sentence()}
- [ ] **Dialogue Authenticity**: ${await lorem.sentence()}

---

## Questions & Further Research

### Unanswered Questions
1. ${await lorem.sentence()}
2. ${await lorem.sentence()}
3. ${await lorem.sentence()}

### Next Steps
- ${helpers.arrayElement(['Interview experts', 'Find additional sources', 'Verify information', 'Expand research scope'])}
- ${helpers.arrayElement(['Cross-reference facts', 'Update story elements', 'Consult specialists', 'Review findings'])}

---

**Research Started**: ${(await date.past()).toLocaleDateString()}  
**Last Updated**: ${new Date().toLocaleDateString()}  
**Status**: ${helpers.arrayElement(['In Progress', 'Completed', 'Needs Verification', 'Ready for Application'])}  
**Priority**: ${helpers.arrayElement(['High', 'Medium', 'Low'])}`
}