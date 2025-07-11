import React, { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { ReferenceItem } from '@/data/reference-items';
import { ReferenceItemComponent } from './reference-item';

export interface ReferenceListProps {
  items: ReferenceItem[];
  command: (item: ReferenceItem) => void;
}

export interface ReferenceListRef {
  onKeyDown: (event: KeyboardEvent) => boolean;
}

export const ReferenceList = forwardRef<ReferenceListRef, ReferenceListProps>(
  ({ items, command }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0);

    // Reset selection when items change
    useEffect(() => {
      setSelectedIndex(0);
    }, [items]);

    // Handle keyboard navigation
    const onKeyDown = (event: KeyboardEvent): boolean => {
      if (event.key === 'ArrowUp') {
        setSelectedIndex(prev => Math.max(0, prev - 1));
        return true;
      }

      if (event.key === 'ArrowDown') {
        setSelectedIndex(prev => Math.min(items.length - 1, prev + 1));
        return true;
      }

      if (event.key === 'Enter') {
        const selectedItem = items[selectedIndex];
        if (selectedItem) {
          command(selectedItem);
        }
        return true;
      }

      return false;
    };

    useImperativeHandle(ref, () => ({
      onKeyDown,
    }));

    if (items.length === 0) {
      return (
        <div className="px-3 py-2 text-sm text-muted-foreground">
          No references found
        </div>
      );
    }

    return (
      <div className="max-h-80 overflow-y-auto">
        {items.map((item, index) => (
          <ReferenceItemComponent
            key={item.id}
            item={item}
            isSelected={index === selectedIndex}
            onSelect={() => command(item)}
          />
        ))}
      </div>
    );
  }
);

ReferenceList.displayName = 'ReferenceList';