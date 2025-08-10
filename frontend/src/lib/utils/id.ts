import { v4 as uuidv4 } from 'uuid';

/**
 * Generates a prefixed UUID for different entity types
 * @param prefix - The entity type prefix (e.g., 'prj', 'doc', 'ft', 'tag')
 * @returns A prefixed UUID string
 */
export function generateId(prefix: string): string {
  const uuid = uuidv4().replace(/-/g, '');
  return `${prefix}_${uuid}`;
}

/**
 * Generates project ID
 */
export function generateProjectId(): string {
  return generateId('prj');
}

/**
 * Generates document ID
 */
export function generateDocumentId(): string {
  return generateId('doc');
}

/**
 * Generates file tree item ID
 */
export function generateFileTreeId(): string {
  return generateId('ft');
}

/**
 * Generates tag ID
 */
export function generateTagId(): string {
  return generateId('tag');
}

/**
 * Generates reference index ID
 */
export function generateReferenceIndexId(): string {
  return generateId('idx');
}