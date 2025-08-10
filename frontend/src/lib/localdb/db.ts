import Dexie, { Table } from 'dexie';
import type { Project, Document, FileTreeItem, Tag, ReferenceIndex, Meta } from './types';

class ShuScribeDB extends Dexie {
  projects!: Table<Project, string>;
  documents!: Table<Document, string>;
  fileTree!: Table<FileTreeItem, string>;
  tags!: Table<Tag, string>;
  referenceIndex!: Table<ReferenceIndex, string>;
  meta!: Table<Meta, string>;

  constructor() {
    super('ShuScribeDB');
    this.version(1).stores({
      projects: 'id, title, createdAt, updatedAt',
      documents: 'id, projectId, path, title, updatedAt',
      fileTree: 'id, projectId, type, path, parentId',
      tags: 'id, projectId, name, category',
      referenceIndex: 'id, projectId, version, updatedAt',
      meta: 'key'
    });
  }
}

export const db = new ShuScribeDB();