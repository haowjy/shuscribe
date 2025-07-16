/**
 * Utility functions for converting search index to autocomplete format
 * 
 * NOTE: This was simplified from rich semantic types (character, location, scene, chapter, note)
 * to basic file/folder types for MVP. Rich types can be restored when backend supports
 * semantic classification of story elements.
 * 
 * TODO: Restore rich reference types for storytelling features:
 * - character, location, scene, chapter, note types
 * - Path-based intelligent type detection  
 * - Rich descriptions for story elements
 */

import { SearchItem } from './index';
import { ReferenceItem } from '@/data/reference-items';

// Convert search items to reference items for autocomplete
export function convertSearchToReferenceItems(searchItems: SearchItem[]): ReferenceItem[] {
  return searchItems.map(item => {
    // Determine type based on search item properties
    let type: ReferenceItem['type'] = 'file';
    
    // For now, just use 'file' since ReferenceItem only supports 'file' | 'folder'
    // SearchItem only has 'file' | 'tag' types, so default to 'file'
    type = 'file';
    
    return {
      id: item.id,
      label: item.title.replace(/\s*\(\d+\s+documents?\)$/, ''), // Remove document count from tags
      type: type as 'file' | 'folder',
      path: item.path,
      tags: item.tags
    };
  });
}

// Create reference string from selected item
export function createReferenceString(item: ReferenceItem): string {
  // Use the path if available, otherwise construct from type and label
  if (item.path && item.path.startsWith('@')) {
    return item.path.substring(1); // Remove @ prefix
  }
  
  // Construct reference path based on type
  const baseName = item.label.toLowerCase().replace(/\s+/g, '-');
  
  switch (item.type) {
    case 'folder':
      return `folder/${baseName}`;
    case 'file':
    default:
      return baseName;
  }
}

// Extract reference type from reference string
export function getReferenceType(reference: string): ReferenceItem['type'] {
  if (reference.startsWith('folder/')) return 'folder';
  return 'file';
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
      label: 'Aria Blackwood',
      type: 'file',
      path: 'characters/aria-blackwood',
      tags: ['main-character', 'mage', 'protagonist']
    },
    {
      id: 'char-2',
      label: 'Marcus Stone',
      type: 'file',
      path: 'characters/marcus-stone',
      tags: ['mentor', 'knight', 'supporting']
    },
    {
      id: 'loc-1',
      label: 'The Crystal Tower',
      type: 'file',
      path: 'locations/crystal-tower',
      tags: ['magical', 'tower', 'important']
    },
    {
      id: 'characters',
      label: 'Characters',
      type: 'folder',
      path: 'characters/',
      tags: ['folder']
    },
    {
      id: 'locations',
      label: 'Locations',
      type: 'folder',
      path: 'locations/',
      tags: ['folder']
    }
  ];
}