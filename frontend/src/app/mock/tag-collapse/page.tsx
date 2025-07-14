"use client";

import React, { useState, useRef } from "react";
import useResizeObserver from "@react-hook/resize-observer";
import { 
  ResizablePanelGroup, 
  ResizablePanel, 
  ResizableHandle 
} from "@/components/ui/resizable";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { File } from "lucide-react";
import { cn } from "@/lib/utils";
import { TagDisplay } from "@/components/file-explorer/components/TagDisplay";

// Remove unused icons array since we're using real TagDisplay component

// Mock files with proper tag structure for TagDisplay component
const mockFiles = [
  {
    id: "1",
    name: "character_notes.md",
    tags: [
      { id: "1", name: "Character", icon: "user", color: "#3b82f6", category: "content" },
      { id: "2", name: "World", icon: "globe", color: "#10b981", category: "setting" },
      { id: "3", name: "Important", icon: "star", color: "#f59e0b", category: "priority" }
    ]
  },
  {
    id: "2", 
    name: "very_long_filename_that_should_definitely_truncate_when_space_runs_out.md",
    tags: [
      { id: "4", name: "Love", icon: "heart", color: "#ef4444", category: "emotion" },
      { id: "5", name: "Action", icon: "zap", color: "#8b5cf6", category: "genre" },
      { id: "6", name: "Defense", icon: "shield", color: "#06b6d4", category: "theme" },
      { id: "7", name: "Royal", icon: "crown", color: "#f97316", category: "character" },
      { id: "8", name: "Extra", icon: "star", color: "#84cc16", category: "misc" }
    ]
  },
  {
    id: "3",
    name: "short.md", 
    tags: [
      { id: "9", name: "Single", icon: "star", color: "#f59e0b", category: "priority" }
    ]
  },
  {
    id: "4",
    name: "extremely_long_filename_that_will_test_truncation_behavior_in_narrow_spaces.md",
    tags: [
      { id: "10", name: "Test", icon: "star", color: "#f59e0b", category: "priority" },
      { id: "11", name: "Long", icon: "crown", color: "#f97316", category: "character" }
    ]
  },
  {
    id: "5",
    name: "no_tags.md",
    tags: []
  },
  {
    id: "6",
    name: "single_char.md",
    tags: [
      { id: "12", name: "A", icon: "star", color: "#f59e0b", category: "priority" },
      { id: "13", name: "B", icon: "heart", color: "#ef4444", category: "emotion" },
      { id: "14", name: "C", icon: "zap", color: "#8b5cf6", category: "genre" },
      { id: "15", name: "D", icon: "shield", color: "#06b6d4", category: "theme" }
    ]
  },
  {
    id: "7",
    name: "prologue_chapter_one_the_beginning_of_an_epic_adventure.md",
    tags: [
      { id: "16", name: "Chapter", icon: "book", color: "#8b5cf6", category: "structure" },
      { id: "17", name: "Epic", icon: "star", color: "#f59e0b", category: "tone" },
      { id: "18", name: "Adventure", icon: "compass", color: "#10b981", category: "genre" }
    ]
  },
  {
    id: "8",
    name: "villain_backstory_and_motivation_detailed_analysis.md",
    tags: [
      { id: "19", name: "Villain", icon: "skull", color: "#ef4444", category: "character" },
      { id: "20", name: "Backstory", icon: "history", color: "#8b5cf6", category: "development" },
      { id: "21", name: "Analysis", icon: "search", color: "#06b6d4", category: "process" }
    ]
  },
  {
    id: "9",
    name: "world_building_geography_and_political_systems.md",
    tags: [
      { id: "22", name: "World", icon: "globe", color: "#10b981", category: "setting" },
      { id: "23", name: "Politics", icon: "flag", color: "#f97316", category: "theme" },
      { id: "24", name: "Geography", icon: "map", color: "#06b6d4", category: "setting" }
    ]
  },
  {
    id: "10",
    name: "magic_system_rules_and_limitations_comprehensive_guide.md",
    tags: [
      { id: "25", name: "Magic", icon: "wand", color: "#8b5cf6", category: "system" },
      { id: "26", name: "Rules", icon: "book", color: "#f59e0b", category: "structure" },
      { id: "27", name: "Guide", icon: "info", color: "#06b6d4", category: "reference" }
    ]
  },
  {
    id: "11",
    name: "dialogue_snippets_and_character_voice_examples.md",
    tags: [
      { id: "28", name: "Dialogue", icon: "message", color: "#10b981", category: "writing" },
      { id: "29", name: "Voice", icon: "mic", color: "#f97316", category: "style" }
    ]
  },
  {
    id: "12",
    name: "research_notes_historical_references_and_sources.md",
    tags: [
      { id: "30", name: "Research", icon: "search", color: "#06b6d4", category: "process" },
      { id: "31", name: "Historical", icon: "history", color: "#8b5cf6", category: "reference" },
      { id: "32", name: "Sources", icon: "link", color: "#10b981", category: "reference" }
    ]
  },
  {
    id: "13",
    name: "plot_outline_major_story_beats_and_character_arcs.md",
    tags: [
      { id: "33", name: "Plot", icon: "trending-up", color: "#f59e0b", category: "structure" },
      { id: "34", name: "Outline", icon: "list", color: "#8b5cf6", category: "planning" },
      { id: "35", name: "Arcs", icon: "activity", color: "#10b981", category: "development" }
    ]
  },
  {
    id: "14",
    name: "scene_by_scene_breakdown_of_climactic_battle_sequence.md",
    tags: [
      { id: "36", name: "Scene", icon: "camera", color: "#f97316", category: "structure" },
      { id: "37", name: "Battle", icon: "sword", color: "#ef4444", category: "action" },
      { id: "38", name: "Climax", icon: "zap", color: "#f59e0b", category: "plot" }
    ]
  },
  {
    id: "15",
    name: "thematic_elements_symbolism_and_deeper_meanings.md",
    tags: [
      { id: "39", name: "Theme", icon: "lightbulb", color: "#f59e0b", category: "analysis" },
      { id: "40", name: "Symbol", icon: "eye", color: "#8b5cf6", category: "literary" },
      { id: "41", name: "Meaning", icon: "brain", color: "#06b6d4", category: "analysis" }
    ]
  },
  {
    id: "16",
    name: "romance_subplot_relationship_development_timeline.md",
    tags: [
      { id: "42", name: "Romance", icon: "heart", color: "#ef4444", category: "subplot" },
      { id: "43", name: "Timeline", icon: "clock", color: "#10b981", category: "structure" }
    ]
  },
  {
    id: "17",
    name: "editing_notes_revision_history_and_feedback_compilation.md",
    tags: [
      { id: "44", name: "Editing", icon: "edit", color: "#8b5cf6", category: "process" },
      { id: "45", name: "Revision", icon: "refresh", color: "#f97316", category: "process" },
      { id: "46", name: "Feedback", icon: "message-circle", color: "#06b6d4", category: "input" }
    ]
  },
  {
    id: "18",
    name: "character_relationship_matrix_and_interaction_dynamics.md",
    tags: [
      { id: "47", name: "Character", icon: "user", color: "#3b82f6", category: "content" },
      { id: "48", name: "Relations", icon: "users", color: "#10b981", category: "dynamics" },
      { id: "49", name: "Matrix", icon: "grid", color: "#8b5cf6", category: "structure" }
    ]
  },
  {
    id: "19",
    name: "publishing_strategy_market_analysis_and_submission_guidelines.md",
    tags: [
      { id: "50", name: "Publishing", icon: "book-open", color: "#f59e0b", category: "business" },
      { id: "51", name: "Market", icon: "trending-up", color: "#10b981", category: "analysis" },
      { id: "52", name: "Strategy", icon: "target", color: "#ef4444", category: "planning" }
    ]
  },
  {
    id: "20",
    name: "inspiration_mood_board_visual_references_and_aesthetic_notes.md",
    tags: [
      { id: "53", name: "Inspiration", icon: "star", color: "#f59e0b", category: "creative" },
      { id: "54", name: "Visual", icon: "eye", color: "#8b5cf6", category: "reference" },
      { id: "55", name: "Aesthetic", icon: "palette", color: "#f97316", category: "style" }
    ]
  },
  {
    id: "21",
    name: "beta_reader_feedback_summary_and_actionable_improvements.md",
    tags: [
      { id: "56", name: "Beta", icon: "test-tube", color: "#06b6d4", category: "testing" },
      { id: "57", name: "Feedback", icon: "message-circle", color: "#10b981", category: "input" },
      { id: "58", name: "Improve", icon: "trending-up", color: "#f59e0b", category: "development" }
    ]
  },
  {
    id: "22",
    name: "sequel_ideas_expanded_universe_and_franchise_potential.md",
    tags: [
      { id: "59", name: "Sequel", icon: "fast-forward", color: "#8b5cf6", category: "expansion" },
      { id: "60", name: "Universe", icon: "globe", color: "#10b981", category: "world" },
      { id: "61", name: "Franchise", icon: "building", color: "#f97316", category: "business" }
    ]
  },
  {
    id: "23",
    name: "pacing_analysis_chapter_length_and_narrative_rhythm.md",
    tags: [
      { id: "62", name: "Pacing", icon: "clock", color: "#10b981", category: "structure" },
      { id: "63", name: "Rhythm", icon: "music", color: "#f97316", category: "style" }
    ]
  },
  {
    id: "24",
    name: "q.txt",
    tags: [
      { id: "64", name: "Quick", icon: "zap", color: "#f59e0b", category: "temp" }
    ]
  },
  {
    id: "25",
    name: "temporary_draft_ideas_and_random_thoughts.md",
    tags: [
      { id: "65", name: "Draft", icon: "edit", color: "#8b5cf6", category: "temp" },
      { id: "66", name: "Ideas", icon: "lightbulb", color: "#f59e0b", category: "creative" },
      { id: "67", name: "Random", icon: "shuffle", color: "#06b6d4", category: "misc" }
    ]
  },
  {
    id: "26",
    name: "world_building_geography_and_political_systems.md",
    tags: [
      { id: "68", name: "World", icon: "globe", color: "#10b981", category: "setting" },
      { id: "69", name: "Politics", icon: "flag", color: "#f97316", category: "theme" },
      { id: "70", name: "Geography", icon: "map", color: "#06b6d4", category: "setting" }
    ]
  },
  {
    id: "27",
    name: "chapter_01_the_awakening_detailed_scene_breakdown.md",
    tags: [
      { id: "71", name: "Chapter", icon: "book-open", color: "#8b5cf6", category: "structure" },
      { id: "72", name: "Awakening", icon: "sunrise", color: "#f59e0b", category: "beginning" },
      { id: "73", name: "Scene", icon: "camera", color: "#f97316", category: "detail" }
    ]
  },
  {
    id: "28",
    name: "editing_notes_revision_history_and_feedback_compilation.md",
    tags: [
      { id: "74", name: "Editing", icon: "edit", color: "#8b5cf6", category: "process" },
      { id: "75", name: "Revision", icon: "refresh", color: "#f97316", category: "process" },
      { id: "76", name: "Feedback", icon: "message-circle", color: "#06b6d4", category: "input" }
    ]
  },
  {
    id: "29",
    name: "final_notes.txt",
    tags: []
  },
  {
    id: "30",
    name: "research_references_sources_and_bibliography.md",
    tags: [
      { id: "77", name: "Research", icon: "search", color: "#06b6d4", category: "process" },
      { id: "78", name: "Sources", icon: "link", color: "#10b981", category: "reference" }
    ]
  }
];

// Remove TagIcon function since we'll use real TagDisplay component

// Exact replica of FileTreeItem structure using Button
function ExactFileTreeItemWithButton({ file, containerWidth, depth = 0 }: { file: any; containerWidth: number; depth?: number }) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  
  // Use exact same responsive logic as FileTreeItem
  const getResponsiveState = () => {
    if (containerWidth > 180) {
      return { maxVisibleTags: 3, breakpoint: 'lg' as const, indentScale: 1.0 };
    } else if (containerWidth > 120) {
      return { maxVisibleTags: 2, breakpoint: 'md' as const, indentScale: 0.9 };
    } else if (containerWidth > 80) {
      return { maxVisibleTags: 1, breakpoint: 'sm' as const, indentScale: 0.8 };
    } else {
      return { maxVisibleTags: 0, breakpoint: 'xs' as const, indentScale: 0.7 };
    }
  };
  
  const { maxVisibleTags, breakpoint, indentScale } = getResponsiveState();
  const baseIndent = depth * 12 + 4;
  const scaledIndent = baseIndent * indentScale;
  const showTags = maxVisibleTags > 0;
  const isNarrow = breakpoint === 'xs' || breakpoint === 'sm';

  return (
    <div>
      {/* Exact group wrapper from FileTreeItem */}
      <div className="group w-full overflow-hidden">
        <Button
          ref={buttonRef}
          variant="tree-item"
          className={cn(
            "w-full h-auto text-sm flex items-center justify-start overflow-hidden",
            "transition-colors gap-0",
            isNarrow ? "px-0.5 py-0.5" : "px-1 py-1"
          )}
          style={{ paddingLeft: `${scaledIndent}px` }}
        >
          {/* File/Folder Icons - exact same structure */}
          <div className="flex items-center flex-shrink-0">
            <div className={cn(
              "flex-shrink-0",
              isNarrow ? "w-2.5 mr-0.5" : "w-3 mr-1"
            )} />
            <File className={cn(
              "text-muted-foreground flex-shrink-0",
              isNarrow ? "h-3 w-3" : "h-4 w-4"
            )} />
          </div>
          
          {/* File Name - exact same structure */}
          <Tooltip>
            <TooltipTrigger asChild>
              <span className={cn(
                "flex-1 text-left cursor-inherit overflow-hidden",
                "whitespace-nowrap text-ellipsis min-w-0",
                "shrink-[999]",
                isNarrow && "text-xs"
              )}
              style={{ 
                minWidth: "0px",
                flexShrink: 999
              }}
              >
                {file.name}
              </span>
            </TooltipTrigger>
            <TooltipContent side="bottom" align="start" className="max-w-80">
              <div className="space-y-1">
                <div className="font-medium">{file.name}</div>
                {file.tags && file.tags.length > 0 && (
                  <div className="text-xs">
                    <span className="text-muted-foreground">Tags: </span>
                    {file.tags.map((tag: any) => tag.name).filter(Boolean).join(', ')}
                  </div>
                )}
                <div className="text-xs text-muted-foreground">
                  Container: {containerWidth.toFixed(0)}px • {breakpoint} • Indent: {scaledIndent}px
                </div>
              </div>
            </TooltipContent>
          </Tooltip>
          
          {/* Tags section - using real TagDisplay component */}
          {showTags && (
            <div className="ml-2">
              <TagDisplay
                tags={file.tags}
                maxVisible={maxVisibleTags}
                onTagClick={(tagName) => console.log('Tag clicked:', tagName)}
              />
            </div>
          )}
        </Button>
      </div>
    </div>
  );
}

// Removed SimpleTestRowWithDiv - not needed for testing

// Test container WITHOUT ScrollArea to isolate the issue
function TestContainerWithoutScrollArea({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(200);
  
  useResizeObserver(containerRef, (entry) => {
    if (typeof window !== 'undefined') {
      const width = entry.contentRect.width;
      setContainerWidth(width);
    }
  });

  return (
    <TooltipProvider>
      <div ref={containerRef} className="h-full flex flex-col w-full overflow-hidden">
        {/* Header info */}
        <div className="p-2 text-xs text-muted-foreground border-b">
          Container width: {containerWidth.toFixed(0)}px | NO SCROLL AREA
        </div>
        
        {/* Test WITHOUT ScrollArea - direct div container */}
        <div className="flex-1 p-1 w-full overflow-auto">
          <div className="space-y-1">
            {React.Children.map(children, (child) => 
              React.isValidElement(child) 
                ? React.cloneElement(child, { containerWidth } as any)
                : child
            )}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

// Test container WITH ScrollArea but modified viewport
function TestContainerWithModifiedScrollArea({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(200);
  
  useResizeObserver(containerRef, (entry) => {
    if (typeof window !== 'undefined') {
      const width = entry.contentRect.width;
      setContainerWidth(width);
    }
  });

  return (
    <TooltipProvider>
      <div ref={containerRef} className="h-full flex flex-col w-full overflow-hidden">
        {/* Header info */}
        <div className="p-2 text-xs text-muted-foreground border-b">
          Container width: {containerWidth.toFixed(0)}px | MODIFIED SCROLL AREA
        </div>
        
        {/* Test WITH ScrollArea but no overflow constraints */}
        <ScrollArea className="flex-1 p-1 w-full">
          <div className="space-y-1">
            {React.Children.map(children, (child) => 
              React.isValidElement(child) 
                ? React.cloneElement(child, { containerWidth } as any)
                : child
            )}
          </div>
        </ScrollArea>
      </div>
    </TooltipProvider>
  );
}

// Original exact replica for comparison
function ExactFileExplorerContainer({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(200);
  
  useResizeObserver(containerRef, (entry) => {
    if (typeof window !== 'undefined') {
      const width = entry.contentRect.width;
      setContainerWidth(width);
    }
  });

  return (
    <TooltipProvider>
      <div ref={containerRef} className="h-full flex flex-col w-full overflow-hidden">
        {/* Header info */}
        <div className="p-2 text-xs text-muted-foreground border-b">
          Container width: {containerWidth.toFixed(0)}px | EXACT REPLICA
        </div>
        
        {/* Exact FileExplorer structure: ScrollArea + space-y-1 */}
        <ScrollArea className="flex-1 p-1 w-full overflow-hidden">
          <div className="space-y-1">
            {React.Children.map(children, (child) => 
              React.isValidElement(child) 
                ? React.cloneElement(child, { containerWidth } as any)
                : child
            )}
          </div>
        </ScrollArea>
      </div>
    </TooltipProvider>
  );
}

export default function TagCollapseMockPage() {
  const [panelSize, setPanelSize] = useState(30);

  return (
    <div className="h-screen w-full p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">FileExplorer Truncation Issue Test</h1>
        <p className="text-sm text-muted-foreground mb-4">
          Panel size: {panelSize.toFixed(1)}% | Exact FileExplorer structure replica
        </p>
      </div>

      <ResizablePanelGroup direction="horizontal" className="h-[800px] border rounded">
        <ResizablePanel 
          defaultSize={30} 
          minSize={15}
          onResize={(size) => setPanelSize(size)}
        >
          <div className="h-full flex flex-col">
            {/* Test 1: Exact Replica (with ScrollArea overflow-hidden) */}
            <div className="h-64 border-b">
              <ExactFileExplorerContainer>
                {mockFiles.map(file => (
                  <ExactFileTreeItemWithButton key={`exact-${file.id}`} file={file} containerWidth={0} depth={0} />
                ))}
              </ExactFileExplorerContainer>
            </div>
            
            {/* Test 2: Modified ScrollArea (no overflow-hidden) */}
            <div className="h-64 border-b">
              <TestContainerWithModifiedScrollArea>
                {mockFiles.map(file => (
                  <ExactFileTreeItemWithButton key={`mod-scroll-${file.id}`} file={file} containerWidth={0} depth={0} />
                ))}
              </TestContainerWithModifiedScrollArea>
            </div>
            
            {/* Test 3: No ScrollArea (direct div) */}
            <div className="h-64">
              <TestContainerWithoutScrollArea>
                {mockFiles.map(file => (
                  <ExactFileTreeItemWithButton key={`no-scroll-${file.id}`} file={file} containerWidth={0} depth={0} />
                ))}
              </TestContainerWithoutScrollArea>
            </div>
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <ResizablePanel defaultSize={70}>
          <div className="h-full p-4 bg-muted/20">
            <h2 className="font-semibold mb-4">Container Constraint Testing</h2>
            <ul className="space-y-2 text-sm">
              <li>• <strong>Top section:</strong> Exact FileExplorer replica with ScrollArea + overflow-hidden (PROBLEM)</li>
              <li>• <strong>Middle section:</strong> ScrollArea without overflow-hidden constraint (POTENTIAL FIX)</li>
              <li>• <strong>Bottom section:</strong> NO ScrollArea - direct div.overflow-auto (BASELINE)</li>
              <li>• <strong>Goal:</strong> Identify which container is preventing text truncation</li>
            </ul>
            
            <div className="mt-8">
              <h3 className="font-semibold mb-2">Expected Results</h3>
              <div className="text-sm space-y-2">
                <div className="p-2 rounded bg-green-50 border border-green-200">
                  <strong>If TOP works:</strong> ScrollArea viewport is the constraint
                </div>
                <div className="p-2 rounded bg-yellow-50 border border-yellow-200">
                  <strong>If MIDDLE works:</strong> ScrollArea overflow-hidden is the issue
                </div>
                <div className="p-2 rounded bg-red-50 border border-red-200">
                  <strong>If NONE work:</strong> Issue is deeper in Button/Badge flex behavior
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Container Structure</h3>
              <div className="text-xs text-muted-foreground font-mono bg-gray-50 p-2 rounded">
                TooltipProvider<br/>
                └─ div.h-full.flex.flex-col.w-full.overflow-hidden<br/>
                &nbsp;&nbsp;&nbsp;└─ ScrollArea.flex-1.p-1.w-full.overflow-hidden<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ div.space-y-1<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ div.group.w-full.overflow-hidden<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ Button[variant="tree-item"]<br/>
              </div>
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}