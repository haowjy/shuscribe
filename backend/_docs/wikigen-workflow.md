# WikiGen Workflow: Agent-Based Story Processing and Wiki Generation

## ⚠️ Implementation Status

**Current Status:** The workflow described below represents the **updated architecture** for ShuScribe's WikiGen story processing and wiki generation system, incorporating lessons learned and improved design patterns.

**What's Currently Available:**
- ✅ LLM integration framework with BYOK support
- ✅ Repository pattern supporting both web and local deployments
- ✅ Story and chapter data models
- ✅ Prompt management system with TOML configuration
- 🔄 Agent-based processing architecture (in development)
- 🔄 Arc-based processing and spoiler prevention (planned)
- ❌ Complete end-to-end workflow execution

**Key Improvements:**
- Arc-based processing for handling long stories
- Spoiler-prevention wiki archiving system  
- Specialized agent architecture for different tasks
- Bidirectional chapter-wiki linking
- Web search integration for references and allusions

---

## 1. Overview

The WikiGen workflow transforms unstructured narrative text into comprehensive, interconnected wiki systems through a sophisticated agent-based architecture. The system processes stories incrementally by narrative arcs, ensuring spoiler-free access and enabling continuous updates as new chapters are added.

### Core Innovation: Arc-Based Processing with Spoiler Prevention

Unlike traditional wiki systems that process entire works at once, WikiGen creates **arc-specific wiki archives** that allow readers to safely access wiki content without spoilers:

```
Story Progress: [Ch1][Ch2]...[Ch10][Ch11]...[Ch20][Ch21]...
├── Arc 1 Wiki (Ch1-10)  ← Safe for readers up to Ch10
├── Arc 2 Wiki (Ch1-20)  ← Safe for readers up to Ch20  
└── Arc 3 Wiki (Ch1-30)  ← Safe for readers up to Ch30
```

### Agent Architecture

The workflow employs 5 specialized agents, each optimized for specific tasks:

1. **ArcSplitter Agent**: Analyzes story structure and determines optimal arc boundaries
2. **GeneralSummarizer Agent**: Creates summaries of any content (utility agent)
3. **WikiPlanner Agent**: Plans wiki structure and article organization (fresh/update modes)
4. **ArticleWriter Agent**: Generates wiki content with web search integration (write/update modes)
5. **ChapterBacklinker Agent**: Creates bidirectional links between chapters and wiki articles

---

## 2. Workflow Flow

### 2.1 Complete Workflow Flow

```
[Story Input] 
    ↓
[ArcSplitter] → Arc Boundaries + Token Counts
    ↓
[For Each Arc]
    ↓
[WikiPlanner] → Article Plans + Structure
    ↓
[ArticleWriter] → Wiki Content (with web search)
    ↓
[Save Arc Wiki Archive]
    ↓
[ChapterBacklinker] → Enhanced Chapters
    ↓
[Next Arc or Complete]
```

### 2.2 Update Flow (New Chapters Added)

```
[New Chapters Added]
    ↓
[ArcSplitter] → Reassess Arc Boundaries  
    ↓
[WikiPlanner (update mode)] → Update Plans
    ↓
[ArticleWriter (update mode)] → Updated Content
    ↓
[Save New Arc Wiki Archive]
    ↓
[ChapterBacklinker] → Update Chapter Links
```

---

## 3. Agent Details

### 3.1 ArcSplitter Agent

**Purpose**: Analyzes story structure to determine optimal narrative arc boundaries for wiki generation.

**Input**: 
- Full story content
- Total chapter count
- Story metadata (title, genre, etc.)

**Processing**:
- Analyzes narrative structure and pacing
- Identifies natural story breaks and conclusions
- Considers token count constraints (20k-100k tokens per arc)
- For short stories (<20k tokens), creates single arc

**Output**: 
```xml
<ArcAnalysis>
  <StoryStats>
    <TotalTokens>85000</TotalTokens>
    <RecommendedArcs>3</RecommendedArcs>
    <ArcStrategy>Story has clear three-act structure</ArcStrategy>
  </StoryStats>
  <Arcs>
    <Arc id="1">
      <Title>The Awakening</Title>
      <StartChapter>1</StartChapter>
      <EndChapter>8</EndChapter>
      <Summary>Introduction and first major conflict</Summary>
      <KeyEvents>Character introductions, inciting incident</KeyEvents>
    </Arc>
    <!-- Additional arcs -->
  </Arcs>
</ArcAnalysis>
```

### 3.2 GeneralSummarizer Agent

**Purpose**: Utility agent for creating summaries of any content type.

**Capabilities**:
- Arc summaries for context passing
- Character development tracking
- Previous wiki content summarization
- Story progression summaries

**Input**: Any text content + summarization instructions
**Output**: Structured summaries in requested format

### 3.3 WikiPlanner Agent

**Purpose**: Plans wiki structure and article organization.

**Modes**:
- **Fresh Mode**: Plans entirely new wiki for first arc
- **Update Mode**: Plans updates to existing wiki for subsequent arcs

**Input (Fresh Mode)**:
- Arc content (chapters for current arc)
- Story metadata
- Arc analysis results

**Input (Update Mode)**:
- Arc content (new chapters)
- Previous arc summaries
- Existing wiki structure
- Previous wiki articles

**Processing**:
- Determines article types needed (characters, locations, concepts, etc.)
- Plans article structure and organization
- Identifies cross-referencing opportunities
- Plans file structure and naming conventions

**Output**:
```xml
<WikiPlan>
  <Articles>
    <Article title="Story Wiki" type="main" file="Story_Wiki.md">
      <Preview>Main wiki page summarizing the story</Preview>
      <Structure>
        # Synopsis
        # Characters
        # Plot Summary
        ## Arc 1: The Awakening
      </Structure>
    </Article>
    <Article title="Character Name" type="character" file="characters/Character_Name.md">
      <Preview>Character description</Preview>
      <Structure>
        # Overview
        # History  
        # Relationships
        # Development
      </Structure>
    </Article>
    <!-- Additional articles -->
  </Articles>
</WikiPlan>
```

### 3.4 ArticleWriter Agent

**Purpose**: Generates actual wiki content with web search integration.

**Modes**:
- **Write Mode**: Creates new articles from scratch
- **Update Mode**: Updates existing articles with new information

**Key Features**:
- **Web Search Integration**: Researches allusions, references, and cultural context
- **Consistency Tracking**: Maintains character development and story consistency
- **Cross-referencing**: Automatically creates wiki-style links between articles

**Input**:
- Article plan and structure
- Story content (current arc)
- Overall wiki plan (for linking context)
- Previous article content (update mode only)

**Processing**:
1. **Research Phase**: Web search for relevant context and references
2. **Content Generation**: Create comprehensive article content
3. **Consistency Check**: Ensure consistency with previous content
4. **Link Integration**: Add appropriate wiki-style links

**Output**: Complete Markdown articles with wiki-style linking

### 3.5 ChapterBacklinker Agent

**Purpose**: Creates bidirectional links between chapters and wiki articles.

**Input**:
- Original chapter content
- Generated wiki articles
- Entity mapping (characters, locations, concepts)

**Processing**:
1. **Entity Detection**: Identify wiki-relevant entities in chapters
2. **Context Analysis**: Determine appropriate linking opportunities
3. **Link Generation**: Create markdown-style wiki links
4. **Format Preservation**: Maintain chapter readability

**Output**: Enhanced chapter content with wiki-style backlinks

**Example Transformation**:
```markdown
# Before
Elara walked through the ancient forest, thinking about her mentor's words.

# After  
[[Elara]] walked through the [[Whispering Woods]], thinking about [[Master Aldric]]'s words.
```

---

## 4. Spoiler Prevention & Archive System

### 4.1 Arc-Based Wiki Archives

Each processed arc creates a complete wiki archive that covers the story **up to that arc's endpoint**:

```
story_wiki/
├── arc_1_wiki/          # Safe for readers through Chapter 10
│   ├── Main_Wiki.md
│   ├── characters/
│   ├── locations/
│   └── meta.json
├── arc_2_wiki/          # Safe for readers through Chapter 20
│   ├── Main_Wiki.md
│   ├── characters/
│   ├── locations/
│   └── meta.json
└── arc_3_wiki/          # Safe for readers through Chapter 30
    ├── Main_Wiki.md
    ├── characters/
    ├── locations/
    └── meta.json
```

### 4.2 Progressive Disclosure

Readers can access wiki content appropriate to their reading progress:
- Reading Chapter 5? Use Arc 1 wiki
- Reading Chapter 15? Use Arc 2 wiki  
- Finished Chapter 25? Use Arc 3 wiki

### 4.3 Character Development Tracking

Each wiki archive includes character development sections tracking changes over time:

```markdown
# Character: Elara

## Development Timeline
### Arc 1 (Chapters 1-10)
- Naive village girl discovers her powers
- Hesitant to leave home

### Arc 2 (Chapters 11-20)  
- Gains confidence through trials
- Forms strong friendships
- [Content only visible in Arc 2+ wikis]

### Arc 3 (Chapters 21-30)
- Becomes a leader
- Makes difficult moral choices
- [Content only visible in Arc 3+ wikis]
```

---

## 5. Technical Implementation

### 5.1 Agent Orchestration

The `WikiGenOrchestrator` manages the complete workflow:

```python
class WikiGenOrchestrator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.arc_splitter = ArcSplitterAgent(llm_service)
        self.summarizer = GeneralSummarizerAgent(llm_service)
        self.wiki_planner = WikiPlannerAgent(llm_service)
        self.article_writer = ArticleWriterAgent(llm_service)
        self.chapter_backlinker = ChapterBacklinkerAgent(llm_service)
    
    async def generate_wiki(self, story: Story) -> WikiResult:
        # 1. Split into arcs
        arcs = await self.arc_splitter.analyze_story(story)
        
        # 2. Process each arc
        for arc in arcs:
            # 3. Plan wiki structure
            plan = await self.wiki_planner.create_plan(
                arc=arc, 
                mode="fresh" if arc.is_first else "update",
                previous_summaries=previous_summaries
            )
            
            # 4. Generate articles
            articles = await self.article_writer.write_articles(
                plan=plan,
                mode="write" if arc.is_first else "update",
                web_search_enabled=True
            )
            
            # 5. Save arc wiki archive
            self.save_arc_wiki(arc, articles)
            
            # 6. Create chapter backlinks
            enhanced_chapters = await self.chapter_backlinker.add_links(
                chapters=arc.chapters,
                wiki_articles=articles
            )
            
            # 7. Update previous summaries for next arc
            previous_summaries = await self.summarizer.summarize_arc(arc, articles)
```

### 5.2 Deployment Flexibility

**Web Deployment**:
- Background processing for each arc
- Progress tracking and status updates
- Persistent storage in Supabase
- User access control for different arc wikis

**Local Deployment**:
- Synchronous processing with real-time feedback
- In-memory processing and storage
- File-based export options
- Complete privacy and offline operation

---

## 6. Output Structure

### 6.1 Generated Wiki Archives

Each arc produces a complete wiki archive:

```
arc_2_wiki/
├── Story_Title_Wiki.md              # Main wiki page
├── characters/
│   ├── Main_Character.md
│   ├── Supporting_Character.md
│   └── index.md
├── locations/
│   ├── Primary_Setting.md
│   ├── Secondary_Location.md
│   └── index.md
├── concepts/
│   ├── Magic_System.md
│   ├── Important_Concept.md
│   └── index.md
├── events/
│   ├── Major_Event.md
│   └── index.md
├── chapters_enhanced/               # Chapters with backlinks
│   ├── chapter_01.md
│   ├── chapter_02.md
│   └── ...
└── meta.json                       # Arc metadata and coverage info
```

### 6.2 Enhanced Chapters

Original chapters enhanced with contextual wiki links:

```markdown
# Chapter 5: The Revelation

[[Elara]] stood at the edge of the [[Whispering Woods]], her [[Staff of Elements]] 
glowing softly in the moonlight. The words of the [[Ancient Prophecy]] echoed in 
her mind as she prepared to face the [[Shadow Wraiths]] that had been plaguing 
[[Millbrook Village]].

She thought of [[Master Aldric]]'s training and the [[Elemental Binding Technique]] 
he had taught her just days before his mysterious disappearance...
```

---

## 7. Benefits of This Architecture

### 7.1 Scalability
- Handles stories of any length through arc-based processing
- Parallel processing opportunities within each arc
- Incremental updates without full reprocessing

### 7.2 User Experience
- Spoiler-free wiki access based on reading progress
- Rich, interconnected content with bidirectional linking
- Enhanced reading experience with contextual information

### 7.3 Maintainability  
- Specialized agents with clear responsibilities
- Modular architecture allowing independent agent improvements
- Comprehensive testing possibilities for each agent

### 7.4 Extensibility
- Easy addition of new agent types
- Flexible prompt system via TOML configuration
- Support for multiple story formats and genres

---

## 8. Future Enhancements

### 8.1 Advanced Features
- **Semantic Search**: Better entity matching and linking
- **Quality Metrics**: Automated wiki quality assessment  
- **Custom Templates**: User-defined article structures
- **Multi-language Support**: International story processing

### 8.2 User Experience
- **Interactive Timeline**: Visual story progression tracking
- **Relationship Graphs**: Character and entity relationship visualization
- **Reading Recommendations**: Based on wiki content analysis
- **Collaborative Editing**: Community-driven wiki improvements

### 8.3 Performance Optimizations
- **Caching Systems**: Reduce redundant LLM calls
- **Batch Processing**: Optimize multiple story handling
- **Smart Scheduling**: Efficient resource utilization
- **Progressive Loading**: Improved user interface responsiveness 