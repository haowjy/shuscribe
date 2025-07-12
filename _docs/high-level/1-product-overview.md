# ShuScribe: Product Overview

**Defining What We Build and Why**

*Internal Development Guide - Phased Approach: Writer Tool → Publishing Platform*

-----

## Product Vision & Phasing Strategy

### Phase 1 (MVP): Writer-Focused Tool

**Target**: Serious fiction writers who need better organization and AI assistance
**Core Value**: ProseMirror-powered writing interface with context-aware AI assistance through intelligent @-references
**Revenue**: Direct SaaS subscriptions from writers ($15-50/month)

### Phase 2 (V2+): Publishing Platform

**Target**: Readers discovering stories through interactive wikis, converting to writers
**Core Value**: Unique auto-generated wikis with chapter backlinking for published stories
**Revenue**: Publishing platform fees + reader subscriptions + writer tool conversions

**Strategic Rationale**: Build the best writing tool first using proven rich-text infrastructure (ProseMirror), then use publishing as user acquisition channel. Readers discover ShuScribe through amazing wiki experiences, realize they want to write their own stories, convert to paying writer tool users.

-----

## User Personas

### Phase 1 (MVP) - Writer-Focused

**Primary: The Web Serial Author**

- Publishes weekly on Royal Road, Wattpad, AO3
- Struggles with continuity across 100+ chapters
- Needs better character/world tracking
- **Pain**: Spending 30% of time looking up previous story details

**Secondary: The Indie Novelist**

- Multi-book series with complex worldbuilding
- Collaborates with editors and beta readers
- **Pain**: Maintaining consistency across books and collaborators

**Tertiary: The Writing Team**

- Co-authors or author-editor partnerships
- **Pain**: Keeping everyone aligned on story details

### Phase 2 (V2+) - Reader Acquisition Pipeline

**The Engaged Reader**

- Discovers ShuScribe through published stories with interactive wikis
- Loves exploring story worlds through connected wiki experiences
- **Conversion Path**: Reader → “I want to organize my own story ideas” → Writer Tool User

**The Aspiring Writer**

- Currently just consumes fiction but has story ideas
- Intimidated by existing writing tools
- **Hook**: “If I can explore this amazing story world, maybe I can build my own”

-----

## Core User Journeys

### Phase 1 MVP Journeys

#### Journey 1: Context-Aware Writing Session

1. **Open Project**: Writer opens current chapter, ProseMirror editor loads with context sidebar auto-populated
2. **@-Reference Writing**: Types `@character/elara` to pull character details into AI context and create navigable reference
3. **AI Assistance**: AI provides suggestions based on established story context from references in document
4. **Consistency Checking**: AI flags when new content contradicts existing character details
5. **Wiki Building**: AI offers to create/update character documents based on new story developments

#### Journey 2: Collaborative Story Development

1. **Share Project**: Invites editor with appropriate permissions
2. **Real-time Editing**: Both work simultaneously with ProseMirror’s built-in collaborative editing
3. **Context Synchronization**: Editor sees same @-referenced context as author through shared reference system
4. **Collaborative Development**: Team builds comprehensive story bible together using structured documents
5. **Consistency Maintenance**: AI ensures all collaborators maintain character voice and plot consistency

### Phase 2 Publishing Platform Journeys

#### Journey 3: Author Publishing with Auto-Wiki

1. **Complete Story Arc**: Author finishes story using Phase 1 ProseMirror-based writing tool
2. **Publish Decision**: Chooses to publish on ShuScribe for reader discovery
3. **Auto-Wiki Generation**: Platform extracts @-references to create reader-facing wiki automatically
4. **Spoiler Management**: System intelligently filters content based on reader progress
5. **Chapter Backlinking**: Published chapters automatically link to relevant wiki entries

#### Journey 4: Reader-to-Writer Conversion

1. **Story Discovery**: Reader finds story on ShuScribe through recommendations
2. **Wiki Engagement**: Explores interactive character sheets and world details while reading
3. **Platform Recognition**: Realizes the story organization quality comes from ShuScribe’s reference system
4. **Writing Interest**: “I want to create a world this detailed and organized”
5. **Tool Trial**: Signs up for writer tool to organize their own story ideas

-----

## Feature Specifications

## Phase 1 (MVP): Core Writer Tool

### ProseMirror-Powered Editor Interface

**Context-Aware @-Reference System** (Core MVP Feature)

- `@character/name` - Creates navigable reference and pulls character details into AI context
- `@location/place` - Reference location information with hover previews and AI awareness
- `@timeline/event` - Include chronological context for consistency checking
- `@worldbuilding/system` - Reference established world rules and magic systems
- ProseMirror’s smart autocomplete shows relevant story elements with rich previews

**AI Chat Integration** (Core MVP Feature)

```
User: "@character/elara what's her relationship with magic?"
AI: Based on your referenced character document, Elara has innate fire magic but fears losing control after accidentally burning her childhood home. She's been suppressing her abilities for 3 years.

User: "Help me write a scene where she first uses magic again"
AI: Here are some approaches that would fit her character arc:
1. Forced by immediate danger to someone she cares about
2. Gradual rediscovery in a safe, controlled environment
3. Accidental release during emotional stress
Which direction feels right for this chapter?
```

**Multiple AI Writing Modes**

- **Chapter Writing**: Prose craft, voice consistency, pacing assistance
- **Character Development**: Psychology, motivations, relationship dynamics
- **World Building**: Logic checking, consistency validation, system coherence
- **Plot Planning**: Structure analysis, conflict escalation, pacing optimization
- **Dialogue Polish**: Character voice, subtext refinement, natural flow

**Acceptance Criteria**:

- [ ] @-references autocomplete from existing documents within 200ms using ProseMirror’s efficient lookup
- [ ] AI chat maintains context awareness of all referenced entities in current document
- [ ] Reference navigation works seamlessly within ProseMirror editor
- [ ] Context updates automatically when references change or are added

### Intelligent Reference Management (Core MVP Feature)

**Automatic Reference Resolution**

```
[User types]: "@elara's mentor, an old man named Marcus who taught her fire magic..."

[System suggests]: I noticed you mentioned Marcus as Elara's mentor. Would you like me to:
□ Create character document for Marcus
□ Link existing Marcus character (if found)
□ Update Elara's character sheet with mentor relationship
[Create] [Link] [Update All] [Skip]
```

**Reference Integrity with ProseMirror**

- ProseMirror’s schema ensures reference nodes maintain structural integrity
- Automatic validation of reference targets during editing
- Visual indicators for broken or missing references
- Batch reference updates when documents are renamed or moved

**Acceptance Criteria**:

- [ ] AI accurately identifies new story elements worthy of documentation
- [ ] Reference suggestions appear within 3 seconds of completing relevant content
- [ ] Reference integrity maintained through document operations (rename, delete, move)
- [ ] User can accept/modify/reject suggestions with single interaction

### Real-Time Collaboration (MVP Feature)

**ProseMirror Native Collaboration**

- Built-in operational transforms for conflict-free collaborative editing
- Shared reference context across all collaborators automatically
- Live cursor positions and selections with user attribution
- Real-time reference resolution and AI context sharing

**Collaborative Context Awareness**

- All users see same @-referenced context through ProseMirror’s shared state
- Shared document structure with collaborative change tracking
- Comments and suggestions tied to specific document positions
- Version history with collaborative attribution

**Acceptance Criteria**:

- [ ] Multiple users can edit same document without data loss using ProseMirror’s collaboration
- [ ] Reference changes sync across all collaborators within 500ms
- [ ] AI suggestions remain relevant during collaborative editing
- [ ] Conflict resolution handles reference changes gracefully

-----

## Phase 2 (V2+): Publishing Platform Features

### Auto-Generated Reader Wikis (Unique Differentiator)

**Reference-Driven Wiki Generation**

- Automatically extract @-references from ProseMirror documents to build comprehensive wikis
- Intelligent spoiler detection based on reference positions and chapter progression
- Progressive content reveals as reader advances through story
- Customizable spoiler policies per author preference

**Chapter Backlinking System** (Killer Feature)

```
[Published Chapter Text in ProseMirror]:
"Elara stepped into the tavern, her emerald eyes scanning for Marcus."

[Automatic Backlinks from @-references]:
- "Elara" → Character sheet with spoiler-safe details
- "tavern" → Location guide with atmosphere and history  
- "Marcus" → Character relationships and background (spoiler-filtered)
```

**Interactive Reading Experience**

- Hover previews for character names and locations powered by reference system
- Expandable lore sections for complex worldbuilding
- Visual relationship maps between characters based on @-references
- Timeline integration showing story chronology from referenced events

### Publishing Workflow (V2+)

**One-Click Publishing from ProseMirror**

- Direct publishing from ProseMirror editor to reader platform
- Automatic extraction of @-references for wiki generation
- Preview how auto-generated wiki appears to readers
- SEO optimization for story and wiki discoverability

**Reader Engagement Analytics**

```
📊 Story Performance Dashboard:
├── Wiki Interactions: 1,247 this week
├── Most Referenced: Character/Elara (456 links), Location/Capital (234 links)
├── Reader Progression: Avg 3.2 wiki clicks per chapter
└── Conversion Metrics: 12% of engaged readers signup for writer tool
```

### Reader-to-Writer Conversion (V2+)

**Discovery Funnel**

- Stories ranked by reference density and wiki quality
- Genre-specific discovery with worldbuilding complexity filters
- Reader reviews highlighting story organization and depth through reference system
- “Built with ShuScribe” branding showcasing reference-driven quality

**Conversion Touchpoints**

- “Create your own story world” CTAs in wiki interfaces
- Free trial offers for readers who heavily engage with reference-rich wikis
- Template galleries showing “stories like this one” organization patterns
- Success stories from reader-turned-writers using reference system

-----

## Technical Architecture Updates

### ProseMirror Foundation

**Core Benefits**:

- **Faster Development**: Leverage battle-tested rich text infrastructure instead of building custom editor
- **Better Performance**: ProseMirror’s optimized document model and efficient text operations
- **Enhanced Collaboration**: Built-in operational transforms for real-time collaborative editing
- **Modular Architecture**: Plugin system allows focus on AI and reference innovations

**Reference Implementation**:

```typescript
// Custom ProseMirror schema with reference nodes
const referenceNode = {
  attrs: {
    referenceType: { default: "file" }, // 'file' | 'tag' | 'filter'
    targetId: { default: null },
    displayText: { default: "" }
  },
  inline: true,
  group: "inline",
  atom: true,
  // ProseMirror handles rendering and interaction
}
```

**AI Integration**:

- ProseMirror plugins extract @-references for AI context automatically
- Real-time document analysis as user types and references
- AI suggestions rendered as ProseMirror decorations
- Context-aware assistance based on referenced entities

### Simplified Data Model

**Document Storage**:

```sql
-- Much simpler with ProseMirror JSON storage
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  path TEXT NOT NULL,
  title TEXT NOT NULL,
  content JSONB NOT NULL, -- ProseMirror document
  word_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Extracted references for fast queries
CREATE TABLE document_references (
  source_document_id UUID REFERENCES documents(id),
  target_id UUID NOT NULL,
  target_type TEXT NOT NULL,
  position_start INTEGER NOT NULL,
  display_text TEXT NOT NULL
);
```

-----

## Updated Success Metrics by Phase

### Phase 1 MVP Metrics

**Core Tool Adoption**:

- @-reference usage: >20 per writing session (reduced from 25 due to ProseMirror efficiency)
- AI chat interactions: >12 per hour of active writing (increased due to better context)
- Reference documents created: >15 per active project
- Collaboration sessions: >50% of projects use real-time editing (increased due to ProseMirror native support)

**User Retention**:

- Day 7 retention: >75% (increased due to better UX)
- Month 1 retention: >55% (increased due to reduced friction)
- Annual subscription renewal: >85% (increased due to collaborative features)

### Phase 2 Publishing Platform Metrics

**Reader Engagement**:

- Wiki interactions per chapter read: >3.0 average (increased due to better reference extraction)
- Time spent on wiki pages: >3.5 minutes average
- Return visits to story wikis: >65% of readers

**Writer Acquisition**:

- Reader-to-writer trial conversion: >10% (increased due to better reference system visibility)
- Reader-to-paid writer conversion: >4%
- Publishing platform monthly active authors: >750

**Platform Growth**:

- Stories with auto-generated wikis: >1500 published
- Reader discovery through wiki browsing: >35% of new readers
- Cross-pollination: readers of Story A trying Story B: >30%

-----

## Updated Technical Implementation Priorities

### Phase 1 MVP Requirements (Reduced Complexity)

**Essential Features**:

- ProseMirror editor with custom reference node schema
- @-reference system with autocomplete using ProseMirror plugins
- AI context extraction from ProseMirror document references
- Real-time collaborative editing using ProseMirror’s native capabilities
- Reference integrity management through ProseMirror transforms

**Performance Targets** (Improved with ProseMirror):

- @-reference response time: <150ms (improved from 200ms)
- AI chat response streaming: <400ms first token (improved due to better context extraction)
- Collaboration sync latency: <200ms (improved with ProseMirror native collaboration)
- Reference resolution time: <5 seconds (improved with ProseMirror efficiency)

### Phase 2 Platform Requirements

**Publishing Infrastructure**:

- Automated wiki generation from ProseMirror @-references
- Spoiler detection and filtering system based on reference positions
- Chapter backlinking with hover previews using reference data
- SEO-optimized story and wiki pages
- Reader analytics and engagement tracking

**Scalability Targets**:

- Support 2000+ published stories (increased due to better performance)
- Handle 15,000+ daily reader wiki interactions
- Process wiki generation for 150+ new stories per month
- Maintain <1.5 second page load times (improved performance target)