import React from 'react';
import { 
  FileIcon, 
  FolderIcon, 
  User, 
  Skull, 
  Building, 
  Landmark, 
  Clock, 
  History, 
  BookOpen 
} from 'lucide-react';
import { ReferenceItem } from '@/data/reference-items';
import { cn } from '@/lib/utils';

interface ReferenceItemProps {
  item: ReferenceItem;
  isSelected: boolean;
  onSelect: () => void;
}

// Icon component map
const IconMap = {
  User,
  Skull,
  Building,
  Landmark,
  Clock,
  History,
  BookOpen,
} as const;

export function ReferenceItemComponent({ item, isSelected, onSelect }: ReferenceItemProps) {
  // Get the appropriate icon component
  const getIconComponent = () => {
    if (item.icon && item.icon in IconMap) {
      const IconComponent = IconMap[item.icon as keyof typeof IconMap];
      return <IconComponent className="h-4 w-4 text-blue-500 flex-shrink-0" />;
    }
    
    // Fallback to default icons
    return item.type === 'file' ? (
      <FileIcon className="h-4 w-4 text-blue-500 flex-shrink-0" />
    ) : (
      <FolderIcon className="h-4 w-4 text-amber-500 flex-shrink-0" />
    );
  };

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-2 text-sm cursor-pointer transition-colors',
        isSelected 
          ? 'bg-accent text-accent-foreground' 
          : 'hover:bg-muted/50'
      )}
      onClick={onSelect}
    >
      {/* Icon */}
      {getIconComponent()}
      
      {/* Label */}
      <span className="flex-1 truncate">{item.label}</span>
      
      {/* Tags */}
      {item.tags && item.tags.length > 0 && (
        <div className="flex gap-1 flex-shrink-0">
          {item.tags.slice(0, 2).map(tag => (
            <span
              key={tag}
              className="px-1.5 py-0.5 text-xs bg-muted/70 text-muted-foreground rounded"
            >
              {tag}
            </span>
          ))}
          {item.tags.length > 2 && (
            <span className="px-1.5 py-0.5 text-xs bg-muted/70 text-muted-foreground rounded">
              +{item.tags.length - 2}
            </span>
          )}
        </div>
      )}
    </div>
  );
}