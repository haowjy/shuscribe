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