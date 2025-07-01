# ShuScribe Business Vision

### 1. Project Vision & Purpose

**Core Concept:** ShuScribe is an intelligent platform that automatically generates a personal, spoiler-free wiki for any serialized fiction narrative. By analyzing a story chapter-by-chapter, it creates a comprehensive, navigable knowledge base that grows with the reader's progress.

**Problem Statement:** Readers of long-form, serialized fiction face a constant struggle with memory recall and spoiler avoidance. Remembering minor characters, past events, or complex terminology is difficult when chapters are released weeks apart. Existing fan-made wikis are often incomplete, outdated, or filled with spoilers, making them unusable for readers who are not fully caught up. ShuScribe solves this by providing an always-current, perfectly synchronized memory aid.

**Target Audience (MVP):**
1.  **Dedicated Serial Fiction Readers:** Individuals who actively follow ongoing works on platforms like Royal Road, Wattpad, Archive of Our Own (AO3), and Substack.
2.  **Technically-Inclined Readers:** Early adopters who are familiar with the concept of an API key and are willing to use their own for a powerful, free service.
3.  **Fiction Authors:** Writers seeking an automated tool to provide their readers with safe, supplementary documentation without the manual effort of maintaining a wiki.
4.  **Local Users & Developers:** Technical users who want to run ShuScribe locally via CLI/API without requiring a database or web interface.

### 2. Value Propositions (MVP)

The ShuScribe MVP delivers immediate and tangible value through four key pillars:

1.  **Automated Wiki Generation:** The core magic of the platform. Users upload their story content, and our secure backend pipeline analyzes it to produce a structured, interlinked wiki with articles on characters, locations, and key terms.
2.  **Personalized Spoiler Prevention:** This is our killer feature. The interface is always aware of a user's reading progress. All wiki content—from popover summaries to full articles—is dynamically filtered to ensure a user *never* sees information from a chapter they haven't read yet.
3.  **Zero-Cost Processing via BYOK (Bring Your Own Key):** The MVP is free to use. Users provide their own LLM API key, which our secure backend uses to process their stories. This gives users full control and transparency over processing costs while allowing us to offer the platform's powerful features for free.
4.  **Flexible Deployment Options:** ShuScribe supports both web-based usage (with Supabase backend) and local CLI/API usage (with in-memory storage) to accommodate different user preferences and technical requirements.
5.  **Instant Contextual Memory Support:** Through an elegant in-line popover system, readers can get immediate, spoiler-free reminders about any narrative element without leaving the reading view, eliminating the need to open new tabs and risk spoilers.

### 3. Feature Overview (MVP)

The MVP is focused on delivering a robust and complete core experience with flexible deployment options.

**Core Functionality:**
*   **Flexible Backend Architecture:** Support for both Supabase-backed web deployment and local in-memory operation via CLI/API.
*   **Secure User Accounts:** Simple email/password registration managed by Supabase (for web deployment).
*   **BYOK API Key Management:** A secure settings system for users to enter and update their LLM API key, which is encrypted and stored safely.
*   **Content Ingestion:** Users can upload stories via direct text input or file uploads (API endpoints implemented).
*   **Automated Processing Pipeline:** The secure backend analyzes the story in logical arcs, extracts entities, and generates Markdown-based wiki articles.
*   **Unified Sidebar:** A companion that provides a list of entities relevant to the current chapter or a progress-aware chat assistant for asking simple questions.

**Current Implementation Status:**
*   ✅ **Backend API Infrastructure:** FastAPI application with health checks and basic endpoints
*   ✅ **Dual Repository System:** Abstract repository pattern supporting both Supabase and in-memory storage
*   ✅ **LLM Integration Framework:** Basic structure for LLM provider management and API key handling
*   ✅ **User Management Schema:** Complete user and API key management schemas and repositories
*   🔄 **Processing Pipeline:** Service layer structure implemented, processing logic in development
*   ❌ **Frontend UI:** Not yet implemented - users interact via API or CLI
*   ❌ **Advanced Wiki Features:** Article generation and linking logic in development

**Features NOT in the MVP:**
To maintain focus, the MVP will not include community features (shared wikis, comments), advanced thematic/plot structure analysis, or author-specific dashboards. These are planned for future phases.

### 4. Strategic Approach (MVP)

**Development Philosophy:**
*   **Secure by Design:** All proprietary logic and user keys are handled on the backend. Security is not an afterthought.
*   **Build a Scalable Foundation:** The architecture is designed from day one to support future growth into a tiered, premium service.
*   **Flexible Deployment:** Support both cloud-based web service and local CLI/API usage to maximize accessibility.
*   **Reader-Centric Experience:** Every design choice prioritizes immersion and the prevention of spoilers.

**Go-to-Market Strategy:**
1.  **Technical Preview:** Begin with CLI/API version for developers and technically-inclined users who can provide early feedback.
2.  **Targeted Outreach:** Engage with active reading communities on platforms like Reddit (e.g., r/ProgressionFantasy, r/litrpg) and Discord servers dedicated to popular web serials where the pain point of memory recall is most acute.
3.  **Author Collaboration:** Partner with a few friendly serial fiction authors to use ShuScribe for their own works, providing them with a valuable tool and generating high-quality showcase wikis for new users.
4.  **Web Interface Launch:** Release the full web interface once UI development is complete.

### 5. Business Model (MVP)

The MVP operates on a pure **Bring Your Own Key (BYOK)** model.

*   **Monetization:** The ShuScribe platform itself is **free to use**. The user provides their own LLM API key and therefore bears the direct cost of processing their stories. Our operational costs are limited to hosting and database services (for web deployment) or zero for local usage.
*   **Path to Profitability:** This model allows us to validate the product and build a user base with minimal financial risk. It establishes the technical foundation for future revenue streams, such as:
    *   **Freemium Tiers:** A future "Premium" subscription where we use our own API keys and absorb the processing cost for a monthly fee.
    *   **Author Services:** Paid tiers for authors offering advanced analytics, dashboards, and deeper integration.
    *   **Enterprise/Local Licenses:** Premium support and features for organizations running ShuScribe locally.

### 6. Success Metrics (MVP)

We will measure the success of the MVP by focusing on adoption, engagement, and technical stability across both deployment modes.

*   **User Adoption:**
    *   Number of API users successfully processing stories locally.
    *   Number of user sign-ups (web deployment).
    *   Percentage of users who successfully enter an API key.
    *   Number of stories successfully uploaded and processed.
*   **User Engagement:**
    *   Ratio of wiki articles generated per story.
    *   API endpoint usage patterns and success rates.
    *   `user_progress` updates (indicating active reading, web deployment).
*   **Technical Performance & Feedback:**
    *   Success rate of the wiki generation pipeline across both deployment modes.
    *   Qualitative feedback gathered from early adopters and author partners to guide Phase 2 development.
*   

### 7. Future Features & Extensions (Phase 2+)

Our long-term vision for ShuScribe extends beyond the core MVP to create an even more dynamic, personalized, and insightful wiki experience. These features will unlock deeper engagement, broader use cases, and advanced monetization opportunities.

#### 7.1 Enhanced User Control & Interaction

*   **Multi-Mode Wiki Generation:**
    *   **Vision:** Empower users with choice and control over the wiki generation process. Instead of a single automated pipeline, users can select a mode that aligns with their desired level of engagement and technical comfort.
    *   **Details:** At the start of a new story's processing, offer distinct options:
        *   **Automated & Spoiler-Safe Mode:** (Current MVP pipeline) Ideal for users who want a hands-off experience and prioritize spoiler prevention above all else, receiving arc-based archives without interruption.
        *   **Guided & Interactive Mode:** Allows users to influence the wiki generation process step-by-step through a conversational interface, making decisions on arc boundaries, article focus, and content refinement. This provides maximum user agency and customization.
        *   **Hybrid Mode:** Combines the interactive planning phase (e.g., user-approved arc boundaries) with automated, hands-off execution for the content generation, offering a balance of control and efficiency.
*   **Conversational Orchestrator:**
    *   **Vision:** Transform the backend into a highly flexible, conversational partner. Instead of rigid agent calls, a central "AI orchestrator" engages in a long-running chat thread with the user, intelligently spawning and managing specialized agents based on user queries and interests.
    *   **Details:** This involves a sophisticated "turn-taking" mechanism where the system understands user intent ("Tell me about Elara," "What's the significance of this event?"), activates the relevant agent (e.g., CharacterAnalysisAgent, PlotAgent), receives its structured output, and then presents it naturally to the user. A shared `WikiGenContext` will maintain the state and accumulated wiki content throughout the conversation. Outputs would dynamically filter based on the user's explicit reading progress to maintain spoiler safety in this interactive mode.
*   **Interactive Arc & Plan Approval:**
    *   **Vision:** Introduce collaborative decision points where the user can review and approve critical structural elements.
    *   **Details:** After the `ArcSplitterAgent` proposes narrative arc boundaries, the system will present these to the user in a visual or textual format. Users can then accept the suggestions or manually adjust the start/end chapters for each arc. Similarly, the `WikiPlannerAgent` could present its proposed article list and structure for user feedback before the `ArticleWriterAgent` begins content generation. This ensures the wiki aligns with the user's interpretation of the story.
*   **Checkpoint-Based Conversation within Arcs:**
    *   **Vision:** Provide an opportunity for deep, spoiler-safe exploration within a completed arc.
    *   **Details:** Once an arc's processing is complete and its spoiler-safe archive is generated, the system can offer a freeform Q&A session. Users can ask detailed questions about characters, locations, events, or themes *within the scope of that arc's content*, without risking spoilers from future arcs. After the user feels satisfied with the current arc's wiki, they can signal "ready," and the system saves the arc wiki as a "checkpoint" and potentially moves to the next arc's processing.
*   **User-Driven Refinement Loops:**
    *   **Vision:** Allow users to iteratively improve specific wiki articles or sections.
    *   **Details:** After an agent presents generated content (e.g., a character profile), the user can provide direct feedback ("Can you add more about their childhood?", "This relationship feels incomplete"). The system would then re-run the relevant agent with the refined instructions, allowing for continuous quality improvement based on user preference.

#### 7.2 Deeper AI Insights & Automation

*   **Dynamic Context Management:**
    *   **Vision:** Enhance agent intelligence by dynamically providing only the most relevant and spoiler-safe contextual information for any given task.
    *   **Details:** A dedicated `ContextManager` component will be developed. When an agent is invoked (e.g., to analyze a character in Arc 2), this manager will intelligently select and filter relevant information from previous arcs (e.g., character's Arc 1 summary, previous world-building details, resolved plot threads) to ensure the agent's output is consistent, comprehensive, and most importantly, does not reveal future spoilers.
*   **Quality Assurance & Metrics Agents:**
    *   **Vision:** Implement automated checks to ensure the high quality and consistency of generated wiki content.
    *   **Details:** Introduce dedicated `WikiQualityChecker` agents that run post-generation validation. These agents would:
        *   **Consistency Checks:** Verify character traits, plot points, and world-building consistency across multiple arcs.
        *   **Completeness Checks:** Assess if all key entities from an arc are covered by articles.
        *   **Cross-Reference Validation:** Ensure all internal wiki links are valid and resolve correctly.
        *   **Style & Format Enforcement:** Verify adherence to Markdown formatting and defined wiki style guides.
        *   **Sentiment/Tone Analysis:** Assess if the generated content matches the story's tone.
*   **Semantic Search & Advanced Information Retrieval:**
    *   **Vision:** Move beyond keyword search to provide intelligent, context-aware information retrieval within the generated wikis and source material.
    *   **Details:** Implement embedding-based semantic search across all wiki articles and enhanced chapters. This allows users to ask natural language questions ("What did Elara do after leaving the Whispering Woods?"), and the system intelligently surfaces the most relevant information, even if exact keywords aren't present.
*   **Custom Templates & Generative Output Control:**
    *   **Vision:** Give users unprecedented control over the *format* and *structure* of their wiki articles.
    *   **Details:** Users could define their own Jinja2 template macros or entire TOML prompt structures for specific article types (e.g., a detailed character sheet, a location description with specific sections like "Flora & Fauna," "History," "Inhabitants"). The `ArticleWriterAgent` would then generate content specifically into these user-defined templates.

#### 7.3 Collaborative & Community Features

*   **Collaborative Editing & Community Curation:**
    *   **Vision:** Evolve ShuScribe from a personal tool into a platform where communities can collectively build and refine wikis for their favorite stories.
    *   **Details:** Implement version control for wiki articles, allowing multiple users to suggest edits. A moderation system would ensure quality and adherence to spoiler policies. This would include user roles (reader, contributor, editor) and discussion forums tied to specific wiki articles.
*   **Shared Wikis & Discovery:**
    *   **Vision:** Allow users to share their generated wikis with others (e.g., a link to a spoiler-safe wiki up to Chapter X), fostering community around shared reading experiences.
    *   **Details:** A discovery platform where users can browse high-quality, community-vetted wikis generated by others. Authors could also "publish" their official ShuScribe wikis.

#### 7.4 Advanced Analytics & Visualization

*   **Interactive Timelines:**
    *   **Vision:** Provide a dynamic, visual representation of the story's progression, correlating plot points, character introductions, and major events across arcs.
    *   **Details:** A UI component that visualizes key story events extracted by agents, allowing users to scroll through the timeline and jump to relevant chapters or wiki articles.
*   **Relationship Graphs:**
    *   **Vision:** Graphically display complex character relationships, faction dynamics, and thematic connections.
    *   **Details:** A knowledge graph built from extracted entities and their relationships, allowing users to visualize networks of characters (friend/foe/family), organizations, and even conceptual links.
*   **Reading Recommendations & Progress Heatmaps:**
    *   **Vision:** Leverage wiki data to provide personalized reading insights and recommendations.
    *   **Details:** Analyze user interaction with the wiki to suggest related stories, or even highlight areas within the current story (e.g., chapters with high activity for a specific character) for re-reading. Progress heatmaps could show a user's engagement with different parts of the story or wiki.