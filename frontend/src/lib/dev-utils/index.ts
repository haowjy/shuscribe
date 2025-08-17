/**
 * Development utilities entry point
 * Provides controlled access to dev-only tools with strict NODE_ENV guards
 */

// Type-only imports for production safety
import type { Project, Document, FileTreeItem, Tag } from '../localdb/types';

// Production-safe exports with runtime guards
export const isDevMode = process.env.NODE_ENV === 'development';

// Lazy-loaded dev utilities with error handling
let devUtils: any = null;

if (isDevMode) {
  try {
    // Dynamic imports to prevent bundling in production
    const contentGenerators = require('./generators/content-generators');
    const markdownParsers = require('./parsers/markdown-parser');
    const contentTemplates = require('./content/templates');
    
    devUtils = {
      ...contentGenerators,
      ...markdownParsers,
      ...contentTemplates,
    };
  } catch (error) {
    console.warn('Dev utilities not available:', error);
  }
}

// Safe wrapper functions with fallbacks
export const seedSampleProject = async (userId?: string): Promise<string> => {
  if (devUtils?.seedSampleProject) {
    return devUtils.seedSampleProject(userId);
  }
  throw new Error('Dev utilities not available in production');
};

export const seedLargeDemo = async (userId?: string): Promise<string> => {
  if (devUtils?.seedLargeDemo) {
    return devUtils.seedLargeDemo(userId);
  }
  throw new Error('Dev utilities not available in production');
};

export const markdownToProseMirror = (markdown: string): Record<string, any> => {
  if (devUtils?.markdownToProseMirror) {
    return devUtils.markdownToProseMirror(markdown);
  }
  throw new Error('Markdown parser not available in production');
};

// Type exports for development
export type DevProject = Partial<Project>;
export type DevDocument = Partial<Document>;
export type DevFileTreeItem = Partial<FileTreeItem>;
export type DevTag = Partial<Tag>;