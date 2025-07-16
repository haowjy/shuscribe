/**
 * Tag management types for the enhanced tagging system
 */

export interface ProjectTag {
  id: string;
  name: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
  usage_count: number;
  last_used?: string;
  is_system: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTagRequest {
  name: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
}

export interface UpdateTagRequest {
  name?: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
  is_archived?: boolean;
}

export interface TagAssignmentRequest {
  tag_ids: string[];
}

// Enhanced tree item with tag objects
export interface EnhancedTreeItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  tag_ids: string[];
  tags: ProjectTag[];
  description?: string;
  color?: string;
  icon?: string;
  path: string;
  parent_id?: string;
  document_id?: string;
  children?: EnhancedTreeItem[];
  created_at: string;
  updated_at: string;
}

// Tag analytics and filtering
export interface TagAnalytics {
  total_tags: number;
  most_used_tags: ProjectTag[];
  unused_tags: ProjectTag[];
  tags_by_category: Record<string, ProjectTag[]>;
}

export interface TagFilterOptions {
  categories?: string[];
  include_archived?: boolean;
  include_system?: boolean;
  sort_by?: 'name' | 'usage_count' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

// UI component interfaces
export interface TagDisplayProps {
  tags: ProjectTag[];
  maxVisible?: number;
  onTagClick?: (tag: ProjectTag) => void;
  showTooltips?: boolean;
}

export interface TagInputProps {
  availableTags: ProjectTag[];
  selectedTagIds: string[];
  onTagsChange: (tagIds: string[]) => void;
  onCreateTag?: (tag: CreateTagRequest) => Promise<ProjectTag>;
  placeholder?: string;
  maxTags?: number;
}

export interface TagManagerProps {
  projectId: string;
  onTagSelect?: (tag: ProjectTag) => void;
  onTagCreate?: (tag: CreateTagRequest) => Promise<ProjectTag>;
  onTagUpdate?: (tagId: string, updates: UpdateTagRequest) => Promise<ProjectTag>;
  onTagDelete?: (tagId: string) => Promise<void>;
}