// Utility functions for converting search index to autocomplete format

import { SearchItem } from './index';
import { ReferenceItem } from '@/components/editor/reference-autocomplete';

// Convert search items to reference items for autocomplete
export function convertSearchToReferenceItems(searchItems: SearchItem[]): ReferenceItem[] {
  return searchItems.map(item => {
    // Determine type based on search item properties
    let type: ReferenceItem['type'] = 'document';
    
    if (item.type === 'tag') {
      type = 'note'; // Tags are treated as notes
    } else if (item.path) {
      // Infer type from path structure
      const pathLower = item.path.toLowerCase();
      if (pathLower.includes('character') || pathLower.includes('char')) {
        type = 'character';
      } else if (pathLower.includes('location') || pathLower.includes('loc')) {
        type = 'location';
      } else if (pathLower.includes('chapter') || pathLower.includes('ch')) {
        type = 'chapter';
      } else if (pathLower.includes('scene')) {
        type = 'scene';
      } else if (pathLower.includes('note')) {
        type = 'note';
      }
    }
    
    return {
      id: item.id,
      name: item.title.replace(/\s*\(\d+\s+documents?\)$/, ''), // Remove document count from tags
      type,
      path: item.path,
      description: item.type === 'tag' ? `Tag found in ${item.title.match(/\((\d+)\s+documents?\)/)?.[1] || '0'} documents` : undefined,
      tags: item.tags
    };
  });
}

// Create reference string from selected item
export function createReferenceString(item: ReferenceItem): string {
  // Use the path if available, otherwise construct from type and name
  if (item.path && item.path.startsWith('@')) {
    return item.path.substring(1); // Remove @ prefix
  }
  
  // Construct reference path based on type
  const baseName = item.name.toLowerCase().replace(/\s+/g, '-');
  
  switch (item.type) {
    case 'character':
      return `character/${baseName}`;
    case 'location':
      return `location/${baseName}`;
    case 'chapter':
      return `chapter/${baseName}`;
    case 'scene':
      return `scene/${baseName}`;
    case 'note':
      return `note/${baseName}`;
    default:
      return baseName;
  }
}

// Extract reference type from reference string
export function getReferenceType(reference: string): ReferenceItem['type'] {
  if (reference.startsWith('character/')) return 'character';
  if (reference.startsWith('location/')) return 'location';
  if (reference.startsWith('chapter/')) return 'chapter';
  if (reference.startsWith('scene/')) return 'scene';
  if (reference.startsWith('note/')) return 'note';
  return 'document';
}

// Format reference name for display
export function formatReferenceName(reference: string): string {
  // Extract the name part after the type prefix
  const parts = reference.split('/');
  if (parts.length > 1) {
    return parts.slice(1).join('/').replace(/-/g, ' ');
  }
  return reference.replace(/-/g, ' ');
}

// Generate mock reference items for testing
export function generateMockReferenceItems(): ReferenceItem[] {
  return [
    {
      id: 'char-1',
      name: 'Aria Blackwood',
      type: 'character',
      path: 'characters/aria-blackwood',
      description: 'Main protagonist, skilled mage',
      tags: ['main-character', 'mage', 'protagonist']
    },
    {
      id: 'char-2',
      name: 'Marcus Stone',
      type: 'character',
      path: 'characters/marcus-stone',
      description: 'Aria\'s mentor and former knight',
      tags: ['mentor', 'knight', 'supporting']
    },
    {
      id: 'loc-1',
      name: 'The Crystal Tower',
      type: 'location',
      path: 'locations/crystal-tower',
      description: 'Ancient tower housing magical artifacts',
      tags: ['magical', 'tower', 'important']
    },
    {
      id: 'loc-2',
      name: 'Whisperwood Forest',
      type: 'location',
      path: 'locations/whisperwood-forest',
      description: 'Mystical forest where spirits dwell',
      tags: ['forest', 'spirits', 'mysterious']
    },
    {
      id: 'ch-1',
      name: 'The Awakening',
      type: 'chapter',
      path: 'chapters/01-the-awakening',
      description: 'First chapter where Aria discovers her powers',
      tags: ['opening', 'discovery', 'powers']
    },
    {
      id: 'scene-1',
      name: 'Battle at the Tower',
      type: 'scene',
      path: 'scenes/battle-at-tower',
      description: 'Climactic battle sequence',
      tags: ['action', 'battle', 'climax']
    },
    {
      id: 'note-1',
      name: 'Magic System',
      type: 'note',
      path: 'notes/magic-system',
      description: 'Notes on how magic works in this world',
      tags: ['worldbuilding', 'magic', 'reference']
    }
  ];
}