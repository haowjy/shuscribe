"use client";

import { useEffect, useState, RefObject } from "react";

export type FileTreeBreakpoint = 'xs' | 'sm' | 'md' | 'lg';

export interface ResponsiveFileTreeState {
  breakpoint: FileTreeBreakpoint;
  width: number;
  maxVisibleTags: number;
  showTags: boolean;
  indentScale: number;
}

// Breakpoint thresholds
const BREAKPOINTS = {
  xs: 160,   // Very narrow - hide all tags, minimal spacing
  sm: 220,   // Narrow - 1 tag max, reduced spacing  
  md: 300,   // Medium - 2 tags, normal spacing
  lg: 400    // Large - 3+ tags, full spacing
} as const;

function getBreakpoint(width: number): FileTreeBreakpoint {
  if (width < BREAKPOINTS.xs) return 'xs';
  if (width < BREAKPOINTS.sm) return 'sm';
  if (width < BREAKPOINTS.md) return 'md';
  return 'lg';
}

function getResponsiveConfig(breakpoint: FileTreeBreakpoint, width: number): Omit<ResponsiveFileTreeState, 'breakpoint' | 'width'> {
  switch (breakpoint) {
    case 'xs':
      return {
        maxVisibleTags: 0,
        showTags: false,
        indentScale: 0.5 // Minimal indentation
      };
    case 'sm':
      return {
        maxVisibleTags: 1,
        showTags: true,
        indentScale: 0.7 // Reduced indentation
      };
    case 'md':
      return {
        maxVisibleTags: 2,
        showTags: true,
        indentScale: 0.85 // Slightly reduced indentation
      };
    case 'lg':
    default:
      return {
        maxVisibleTags: Math.max(2, Math.floor(width / 120)), // Scale with width
        showTags: true,
        indentScale: 1.0 // Full indentation
      };
  }
}

export function useResponsiveFileTree(containerRef: RefObject<HTMLElement | HTMLDivElement | null>): ResponsiveFileTreeState {
  const [state, setState] = useState<ResponsiveFileTreeState>({
    breakpoint: 'lg',
    width: 300,
    maxVisibleTags: 2,
    showTags: true,
    indentScale: 1.0
  });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateSize = () => {
      const rect = container.getBoundingClientRect();
      const width = rect.width;
      const breakpoint = getBreakpoint(width);
      const config = getResponsiveConfig(breakpoint, width);

      setState({
        breakpoint,
        width,
        ...config
      });
    };

    // Initial measurement
    updateSize();

    // Set up ResizeObserver
    const resizeObserver = new ResizeObserver(() => {
      updateSize();
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, [containerRef]);

  return state;
}

// Helper hook for components that need container width tracking
export function useContainerWidth(containerRef: RefObject<HTMLElement | HTMLDivElement | null>): number {
  const [width, setWidth] = useState(300);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateWidth = () => {
      const rect = container.getBoundingClientRect();
      setWidth(rect.width);
    };

    updateWidth();

    const resizeObserver = new ResizeObserver(updateWidth);
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, [containerRef]);

  return width;
}