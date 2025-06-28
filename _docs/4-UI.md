# Frontend UI Vision and User Experience

## ⚠️ Implementation Status

**Current Status:** The UI described in this document represents the **planned vision** for the ShuScribe frontend. The current implementation focuses on the **backend API and processing pipeline**. 

**What's Currently Available:**
- ✅ Complete FastAPI backend with REST API endpoints
- ✅ Both web-ready (Supabase) and local (in-memory) deployment modes
- ✅ User management and API key handling via API
- ✅ Story processing infrastructure
- 🔄 Wiki generation pipeline (in development)
- ❌ Frontend UI (planned for future implementation)

**Current Usage:** Users interact with ShuScribe through direct API calls or CLI commands. The web interface described below will be implemented in a subsequent development phase.

---

### 1. Vision Statement

The ShuScribe user interface is designed to be an **invisible companion** to the reading experience. It prioritizes immersion and clarity, seamlessly integrating a powerful wiki without ever pulling the reader out of the story. Our goal is to empower readers with instant, context-aware knowledge while rigorously protecting them from spoilers. The design is clean, intuitive, and centered on the narrative itself.

### 2. Guiding Principles

1.  **The Reading Experience is Sacred:** The primary interface is the text. All features are designed to enhance, not distract from, the act of reading.
2.  **Context is King:** The UI is always aware of the reader's progress. Every piece of information presented is filtered to match what the reader *should* know at their current chapter.
3.  **Seamless Transition:** Moving between reading the story and exploring the wiki should feel effortless and natural, like turning to a glossary at the back of a book.
4.  **Progressive Disclosure:** Information is revealed in layers. A quick hint is available on demand, with deeper knowledge just one click away, preventing cognitive overload.
5.  **API-First Design:** The UI will be built on top of the existing REST API, ensuring that all functionality remains accessible programmatically.

### 3. The Dual-Mode Interface

The entire experience is built around two distinct but interconnected modes: **Reading Mode** and **Wiki Mode**. A simple, persistent toggle allows the user to switch between them at any time, maintaining their context.

```
┌─────────────────────────────────────────────────────┐
│ [Book Title]        [📖 Reading Mode] | [🔍 Wiki Mode] │
└─────────────────────────────────────────────────────┘
```

---

### 4. Reading Mode: The Immersive Experience

This is the default view and the heart of the application. It presents the chapter text in a clean, readable format, augmented with subtle, powerful tools.

#### 4.1. The Reader View

The layout is minimalist, focusing on typography and readability. The core feature is the **Contextual Entity Reference**.

*   **Subtle Highlighting:** Narrative entities (characters, places, etc.) are not rendered as distracting blue links. Instead, they have a subtle, non-intrusive underline.
*   **Popover on Demand:** When a user hovers over (or taps on) a highlighted entity, a small, elegant popover appears, providing a concise, **spoiler-free** summary.

**Mockup: Reading Mode with Popover**
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│ < Chapter 3: The Crimson Seal                                  > │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ...the council convened in the Sunken City of Aeridor, a place    │
│ few had seen in centuries. General Kaelen stood before the High │
│ Council, his hand resting on the hilt of his blade. He spoke of  │
│ the strange device they had recovered, the one Dr. Aris called   │
│ the "Resonator."                                                 │
│          ──────────                                              │
│              |                                                   │
│              v                                                   │
│   ┌───────────────────────────────────┐                          │
│   │ Dr. Aris                          │                          │
│   │ CHARACTER • RELEVANT              │                          │
│   ├───────────────────────────────────┤                          │
│   │ A sharp-witted scientist from the │                          │
│   │ capital, known for her expertise  │                          │
│   │ in ancient artifacts.             │                          │
│   │                                   │                          │
│   │ [Explore full wiki entry →]       │                          │
│   └───────────────────────────────────┘                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### 4.2. The Unified Sidebar

A collapsible sidebar acts as the reader's companion. It has two tabs:

1.  **Elements:** This tab lists all entities relevant to the *current chapter*, allowing a reader to quickly see who and what is important right now.
2.  **Chat:** A conversational AI assistant, aware of the reader's progress, that can answer questions like "Remind me how Kaelen and Dr. Aris met?" or "Summarize the previous chapter."

**Mockup: Sidebar in Reading Mode**
```
┌────────────────────────┬──────────────────────────────────────────┐
│ ELEMENTS │ CHAT        │                                          │
├────────────────────────┤ ...General Kaelen stood before the High  │
│                        │ Council, his hand resting on the hilt of │
│ RELEVANT TO CHAPTER 3  │ his blade. He spoke of the strange       │
│ ---------------------- │ device they had recovered, the one Dr.   │
│                        │ Aris called the "Resonator."             │
│ CHARACTERS (3)       ▼ │                                          │
│  • General Kaelen      │                                          │
│  • Dr. Aris            │                                          │
│  • High Councilor Roric│                                          │
│                        │                                          │
│ LOCATIONS (1)        ▼ │                                          │
│  • Aeridor             │                                          │
│                        │                                          │
│ TERMINOLOGY (1)      ▼ │                                          │
│  • The Resonator       │                                          │
└────────────────────────┴──────────────────────────────────────────┘
```

---

### 5. Wiki Mode: The Exploration Experience

When a user wants to dive deeper—either by clicking "Explore full wiki entry" or by switching modes manually—they enter Wiki Mode. This is a comprehensive, searchable encyclopedia of the story's world, filtered to their current progress.

#### 5.1. The Wiki Article View

The layout is structured for easy scanning and deep reading.

*   **Clear Navigation:** Breadcrumbs show the user's location within the wiki's hierarchy.
*   **Structured Content:** Articles are generated from Markdown, featuring clear headings, lists, and blockquotes.
*   **Internal Linking:** All `[[Wikilinks]]` are rendered as clickable links, allowing the user to fluidly navigate between related topics.

**Mockup: Wiki Mode Article Page**
```
┌──────────────────────────────────────────────────────────────────┐
│ [Book Title]        [📖 Reading Mode] | [🔍 Wiki Mode]             │
├──────────────────────────────────────────────────────────────────┤
│ [Breadcrumbs: Home > Characters > Dr. Aris]                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ # Dr. Aris                                                       │
│ CHARACTER • RELEVANT • First Appearance: Chapter 2               │
│                                                                  │
│ [Overview | Biography | Relationships]                           │
│                                                                  │
│ Dr. Aris is a brilliant but reclusive archeo-physicist from the  │
│ Royal Institute. She was recruited by [[General Kaelen]] for her │
│ unique knowledge of pre-Collapse artifacts.                      │
│                                                                  │
│ ## Biography                                                     │
│                                                                  │
│ Initially hesitant to join the expedition, Dr. Aris was swayed   │
│ by the discovery of the [[Resonator]], an object she had only    │
│ read about in ancient texts...                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### 5.2. The Sidebar as Wiki Navigation

In Wiki Mode, the sidebar transforms into the primary navigation tool for the entire knowledge base, allowing users to browse the full hierarchy of discovered entities.

**Mockup: Sidebar in Wiki Mode**
```
┌────────────────────────┬──────────────────────────────────────────┐
│ WIKI NAVIGATION        │                                          │
├────────────────────────┤ # Dr. Aris                               │
│ 🔍 Search Wiki...      │                                          │
│ ---------------------- │ CHARACTER • RELEVANT • First App: Ch. 2  │
│                        │                                          │
│ CHARACTERS           ▶ │ [Overview | Biography | Relationships]   │
│ LOCATIONS            ▼ │                                          │
│  • The Capital         │ Dr. Aris is a brilliant but reclusive... │
│  • Aeridor             │                                          │
│  • Kaelen's Outpost    │                                          │
│ FACTIONS             ▶ │                                          │
│ KEY EVENTS           ▶ │                                          │
│ TERMINOLOGY          ▶ │                                          │
└────────────────────────┴──────────────────────────────────────────┘
```

### 6. API Integration and Data Flow

The planned UI will be built as a **client-side application** that consumes the existing ShuScribe REST API:

#### 6.1 Core API Endpoints (Already Implemented)
- `GET /api/v1/health` - System health checks
- `GET /api/v1/llm/providers` - Available LLM providers
- `POST /api/v1/users/api-keys` - Store user API keys (web mode)
- `GET /api/v1/stories/{story_id}` - Retrieve story information
- `GET /api/v1/stories/{story_id}/wiki` - Get wiki articles (filtered by progress)

#### 6.2 Frontend Architecture (Planned)
- **Framework:** Next.js with React for component-based UI
- **State Management:** React Query for server state management
- **Authentication:** Supabase Auth integration (web mode)
- **Styling:** Tailwind CSS for responsive, modern styling
- **Real-time:** WebSocket connections for live updates during processing

### 7. Development Phases

#### Phase 1: Backend Foundation ✅
- REST API implementation
- Repository pattern with dual storage backends
- User management and API key handling
- Basic story processing infrastructure

#### Phase 2: Core Processing 🔄
- Complete wiki generation pipeline
- Entity extraction and linking
- LLM integration and processing logic
- Background task processing (web mode)

#### Phase 3: Basic Web UI ❌
- User authentication and registration
- Story upload interface
- Basic wiki viewing
- Progress tracking

#### Phase 4: Enhanced UI ❌
- Reading mode with entity highlighting
- Interactive popovers and sidebars
- Advanced wiki navigation
- Real-time processing status

#### Phase 5: Advanced Features ❌
- Collaborative features
- Advanced search and filtering
- Author dashboards
- Mobile application

### 8. The User Journey: A Summary

The design supports a fluid and intuitive user journey:

1.  A reader encounters an unfamiliar name (`Dr. Aris`) in **Reading Mode**.
2.  They hover/tap to get an instant, spoiler-free **popover** summary.
3.  Curious for more, they click to seamlessly transition to the full **Wiki Mode** article.
4.  After reading the article, they click on an internal link (`[[General Kaelen]]`) to learn about a related character.
5.  Satisfied, they click the **"Reading Mode"** toggle and are returned to the exact spot in the chapter where they left off, ready to continue the story.

### 9. Current Workarounds

Until the web UI is implemented, users can:
- **API Direct Access:** Use tools like Postman or curl to interact with the API
- **CLI Tools (Planned):** Command-line interface for local story processing
- **Jupyter Notebooks:** Use the provided notebooks for interactive development and testing
- **Custom Integrations:** Build custom clients using the well-documented REST API