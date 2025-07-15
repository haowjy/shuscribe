# AI Collaboration & Conflict Resolution

**Future Feature Specification for Universe-Wide AI Assistance**

*Designing the "Cursor for fiction writing" experience for collaborative AI editing*

---

## Problem Statement

### The AI Collaboration Challenge

**Core Issue**: AI can identify what needs to change across a universe but cannot maintain authorial voice and style.

**Example Scenario**:
- User: "Make sure Elara's eye color is consistent across all chapters"
- AI: Finds 3 inconsistencies across chapters 2, 5, and 7
- Problem: AI suggestions lose the author's unique voice and writing style
- Solution needed: Author controls *how* changes are made, AI finds *what* needs changing

### Two Distinct Conflict Types

**1. Real-Time Collaboration Conflicts**
- Multiple humans editing simultaneously
- Standard solutions: Operational transforms, presence awareness, live cursors
- Well-understood problem with established patterns

**2. AI Collaboration Conflicts (Novel Problem)**
- AI suggests universe-wide changes that affect multiple documents
- Human needs to review and edit AI suggestions before acceptance
- Requires new UX patterns for selective suggestion acceptance
- Must preserve authorial voice while leveraging AI universe understanding

---

## AI Collaboration UX Design

### Core Design Principles

**1. AI as Research Assistant, Not Writer**
- AI identifies inconsistencies, plot holes, character development issues
- AI suggests *what* to change, human controls *how* to change it
- Never auto-apply AI text changes without explicit human approval

**2. Granular Control Over Suggestions**
- Accept, reject, or edit individual suggestions
- Batch operations for similar changes across multiple documents
- Preview changes before application
- Undo/redo for suggestion batches

**3. Voice Preservation**
- AI suggestions serve as starting points for human editing
- Built-in editing interface for refining AI suggestions
- Maintain author's tone, style, and voice in all final changes

### Suggestion Review Interface

```
User Request: "Make sure Elara's eye color is consistent across all chapters"
↓
AI Analysis: Scans @references, finds 3 inconsistencies
↓
Review Interface:

┌─────────────────────────────────────────────────────────────┐
│ Universe Consistency Check: Elara's Eye Color              │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 3 inconsistencies found • 2 accepted • 1 pending          │
│                                                             │
│ ┌─ Chapter 2, Line 45 ──────────────────── ✓ ACCEPTED ──┐ │
│ │ Current: "her blue eyes sparkled"                      │ │
│ │ Applied: "her emerald eyes sparkled"                   │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Chapter 5, Line 123 ─────────────────── ⏸ PENDING ───┐ │
│ │ Current: "looking into her azure gaze"                 │ │
│ │ AI Suggests: "looking into her emerald gaze"           │ │
│ │                                                         │ │
│ │ Your edit: ________________________________             │ │
│ │ "looking into her jade-green gaze"                     │ │
│ │                                                         │ │
│ │ [Accept Edit] [Use AI] [Skip] [Reject]                 │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Apply All Changes] [Save as Draft] [Cancel]               │
└─────────────────────────────────────────────────────────────┘
```

### Progressive Disclosure for Complex Changes

**Simple Changes**: Direct accept/reject interface
**Complex Changes**: Multi-step wizard with context and impact analysis
**Batch Changes**: Grouped by similarity with bulk operations

---

## Technical Architecture

### Data Structures

**AI Suggestion Batch**
```typescript
interface AISuggestionBatch {
  id: string;
  userRequest: string; // "Make Elara's eyes consistent"
  createdAt: Date;
  status: 'analyzing' | 'ready_for_review' | 'in_review' | 'completed' | 'cancelled';
  
  suggestions: AISuggestion[];
  metadata: {
    documentsAffected: string[];
    totalSuggestions: number;
    acceptedCount: number;
    rejectedCount: number;
    pendingCount: number;
  };
}

interface AISuggestion {
  id: string;
  documentId: string;
  documentPath: string;
  location: {
    line: number;
    column: number;
    context: string; // Surrounding text for context
  };
  
  change: {
    original: string;
    aiSuggestion: string;
    userEdit?: string; // If user modified AI suggestion
    finalText?: string; // What was actually applied
  };
  
  status: 'pending' | 'accepted' | 'rejected' | 'edited' | 'applied';
  reasoning: string; // AI explanation for the suggestion
  confidence: number; // AI confidence score
  
  reviewedAt?: Date;
  appliedAt?: Date;
}
```

**Document Change Tracking**
```typescript
interface DocumentVersion {
  id: string;
  documentId: string;
  version: number;
  content: ProseMirrorContent;
  createdAt: Date;
  createdBy: 'user' | 'ai_batch';
  
  // For AI batches
  aiBatchId?: string;
  changesSummary?: string;
  
  // For user edits
  editType?: 'manual' | 'ai_suggestion_accepted' | 'ai_suggestion_edited';
}
```

### AI Suggestion Workflow

**1. User Request Processing**
```
User submits universe-wide request
    ↓
Backend analyzes @references and content
    ↓
AI generates structured suggestions with reasoning
    ↓
Frontend presents review interface
    ↓
User reviews suggestions individually
    ↓
Accepted changes applied as batch
    ↓
Universe index updated with new references
```

**2. Conflict Detection During Review**
```typescript
// Check if documents were modified during AI analysis
const checkForConflicts = async (suggestions: AISuggestion[]) => {
  for (const suggestion of suggestions) {
    const currentDoc = await getDocument(suggestion.documentId);
    const docVersionAtAnalysis = suggestion.metadata.documentVersion;
    
    if (currentDoc.version > docVersionAtAnalysis) {
      // Mark suggestion as potentially stale
      suggestion.status = 'requires_reanalysis';
    }
  }
};
```

### Two-Tier Autosave System

**Tier 1: Normal User Edits**
- Immediate autosave on keystroke pause
- Standard optimistic updates with TanStack Query
- Real-time sync for collaboration

**Tier 2: AI Suggestion Batches**
- Save suggestions as "draft" state during review
- Apply changes only after explicit user acceptance
- Batch commits create new document versions
- Full universe re-indexing after batch application

### Implementation Phases

**Phase 1: Basic AI Suggestions (MVP+1)**
- Simple suggestion interface for single-document changes
- Manual accept/reject for AI suggestions
- Basic version tracking for AI-generated changes

**Phase 2: Universe-Wide Analysis**
- Cross-document consistency checking
- Batch suggestion management
- Advanced review interface with editing capabilities

**Phase 3: Intelligent Conflict Resolution**
- Real-time collaboration awareness during AI review
- Automatic reanalysis when documents change
- Sophisticated merging of AI suggestions with concurrent edits

**Phase 4: Advanced AI Collaboration**
- Predictive suggestions based on writing patterns
- Style-aware AI that learns author voice
- Collaborative AI training on universe-specific patterns

---

## Integration with Existing Architecture

### @-Reference System Integration

**Enhanced Reference Analysis**
- AI uses existing @-reference index for universe-wide analysis
- Suggestions maintain @-reference integrity
- New references created automatically when needed

**Universe Understanding**
- Leverage existing local project index for fast AI context
- AI suggestions update reference mappings
- Cross-reference validation after batch changes

### Frontend-First Architecture Compatibility

**Client-Side Review State**
- Suggestion batches managed in Zustand stores
- Local draft state for review-in-progress
- Optimistic UI updates for accepted suggestions

**Backend API Design**
```typescript
// Frontend defines the expected API
POST /projects/{id}/ai/analyze
{
  request: "Make character descriptions consistent",
  scope: "universe" | "document" | "selection",
  options: AnalysisOptions
}

GET /ai/batches/{batchId}/suggestions
// Returns structured suggestions for review

POST /ai/batches/{batchId}/apply
{
  acceptedSuggestions: string[];
  editedSuggestions: { id: string; finalText: string }[];
  rejectedSuggestions: string[];
}
```

### Publishing Integration

**Wiki Generation Enhancement**
- AI suggestions can trigger wiki regeneration
- Version history includes AI-assisted changes
- Export capabilities include change attribution

**Public Page Updates**
- AI batch changes update published content
- Change logs show AI-assisted improvements
- Reader-facing wikis benefit from AI consistency

---

## Success Metrics

### User Experience Metrics
- **Suggestion Acceptance Rate**: >70% of AI suggestions accepted or edited (not rejected)
- **Time to Review**: <2 minutes per suggestion on average
- **Voice Preservation**: User satisfaction scores for maintaining authorial voice
- **Universe Consistency**: Reduction in continuity errors after AI assistance

### Technical Performance Metrics
- **Analysis Speed**: <30 seconds for universe-wide consistency checks
- **Suggestion Quality**: <20% of suggestions require major editing
- **Conflict Resolution**: <5% of suggestions become stale during review
- **System Reliability**: 99%+ uptime for AI suggestion system

### Adoption Metrics
- **Feature Usage**: >50% of users try AI suggestions within first month
- **Repeat Usage**: >30% of users use AI suggestions weekly
- **Advanced Features**: >20% of users use batch editing capabilities
- **Universe Scale**: AI suggestions work reliably on 100+ document universes

---

## Future Enhancements

### Advanced AI Capabilities
- **Style Learning**: AI adapts to individual author's voice over time
- **Contextual Awareness**: Deep understanding of genre conventions and narrative structure
- **Predictive Suggestions**: Proactive identification of potential issues before they become problems

### Collaborative AI
- **Team AI**: AI assistants that understand team writing styles and preferences
- **Universe Continuity**: AI that maintains franchise-level consistency across multiple authors
- **Editorial AI**: AI that can suggest structural improvements and plot enhancements

### Integration Ecosystem
- **Third-Party Tools**: Integration with grammar checkers, style guides, and publishing platforms
- **Custom AI Models**: Fine-tuned models for specific genres, universes, or writing styles
- **API Extensions**: Developer APIs for custom AI collaboration tools

---

This specification provides the foundation for building AI collaboration features that solve the unique challenges of maintaining authorial voice while leveraging AI's universe-understanding capabilities. The design ensures that ShuScribe becomes truly "Cursor for fiction writing" - providing intelligent assistance that enhances rather than replaces human creativity.