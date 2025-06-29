# Backend Agent Workflows & Technical Implementation

## Overview

ShuScribe's backend employs a sophisticated agent-based architecture where specialized agents handle different aspects of wiki generation. Agents are organized into **workflows** - collections of related agents that work together to accomplish larger goals. This document covers the technical implementation details, naming conventions, and how to extend the system.

## 📋 **Terminology & Naming Conventions**

### **Workflow**
A **workflow** is a collection of related agents that work together to accomplish a larger goal. Each workflow focuses on a specific domain or process.

```
backend/src/agents/
├── wikigen/              # WikiGen Workflow
│   ├── orchestrator.py   # Workflow orchestrator (NOT an agent)
│   ├── arc_splitter_agent.py
│   ├── planner_agent.py
│   ├── article_writer_agent.py
│   └── chapter_backlinker_agent.py
├── future_workflow/      # Future workflows
│   ├── orchestrator.py
│   └── specific_agents.py
├── base_agent.py         # Base agent class
├── prompts/              # Prompt templates
│   ├── wikigen.toml      # Main workflow prompts
│   └── wikigen/          # Workflow-specific prompts
│       ├── _common/      # Shared templates
│       ├── specialized_prompts.toml
│       └── extended_prompts.toml
├── tests/                # Test files
│   └── test_wikigen.py   # Test for WikiGen workflow
```

### **Agent vs Orchestrator**
- **Agent**: Independent, specialized component that can be executed alone given proper inputs
- **Orchestrator**: Coordination layer that manages agents and handles the overall workflow (NOT an agent itself)

### **Naming Standards**
- **Workflow Directory**: `workflow_name/` (e.g., `wikigen/`)
- **Agents**: `{purpose}_agent.py` (e.g., `arc_splitter_agent.py`)
- **Orchestrator**: Always `orchestrator.py` within each workflow
- **Prompts**: `{workflow_name}.toml` (e.g., `wikigen.toml`)

---

## 🎯 **Agent Philosophy**

### **Core Principles**

1. **Independence**: Each agent can be executed standalone with proper inputs
2. **Single Responsibility**: Each agent has one clear, well-defined purpose
3. **Stateless**: Agents don't maintain state between calls
4. **Composable**: Agents can be combined in different ways via orchestrators
5. **Testable**: Each agent can be unit tested in isolation

### **Agent Structure**

```python
# Example Agent Pattern
class SomeAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def execute_main_function(
        self,
        # Clear, typed inputs
        input_data: str,
        context: Optional[str] = None,
        # Required LLM parameters
        user_id: UUID,
        provider: str,
        model: str,
        # Optional parameters with defaults
        mode: str = "default",
        **kwargs
    ) -> AgentResult:
        """
        Main execution function with clear inputs/outputs.
        Should be executable independently given proper inputs.
        """
        # 1. Load and render prompts
        # 2. Make LLM calls
        # 3. Process and validate results
        # 4. Return structured output
        pass
```

### **Agent Independence Requirements**

Each agent must be:
- **Self-contained**: All dependencies clearly specified
- **Input-driven**: Behavior determined by inputs, not internal state
- **Mockable**: Can use mock LLM services for testing
- **Documentable**: Clear documentation of inputs, outputs, and behavior

---

## 📝 **Prompt Management System**

### **TOML Structure**

Prompts are organized in TOML files with a specific hierarchical structure:

```toml
# workflow_name.toml (e.g., wikigen.toml)

[section_name]  # e.g., [arc_splitting], [planning], [generate_article]
name = "Human-readable name"
description = "What this prompt section does"
version = "0.1"
author = "developer_name"

[[section_name.messages]]
role = "system"
content = """System prompt content with Jinja2 templating support"""

[[section_name.messages]] 
role = "user"
content = """User prompt with template variables like {{ story_title }}"""

# Additional configuration
[section_name.config]
temperature = 0.7
max_tokens = 4000
```

### **Template System**

ShuScribe uses **Jinja2** for prompt templating with these features:

#### **Variable Substitution**
```toml
content = """Analyze this story titled "{{ story_title }}" 
with {{ total_chapters }} chapters."""
```

#### **Conditional Logic**
```toml
content = """{% if mode == "update" %}
Update the existing wiki article:
{{ existing_content }}
{% else %}
Create a new wiki article for:
{% endif %}
{{ story_content }}"""
```

#### **Loops and Lists**
```toml
content = """Previous arcs:
{% for arc in previous_arcs %}
- Arc {{ arc.number }}: {{ arc.title }}
{% endfor %}"""
```

### **Shared Templates and Imports**

#### **Common Templates Directory**
```
backend/src/prompts/
├── wikigen.toml              # Main workflow prompts
├── wikigen/
│   ├── _common/              # Shared templates
│   │   ├── character_template.jinja2
│   │   ├── location_template.jinja2
│   │   └── base_instructions.jinja2
│   ├── specialized_prompts.toml
│   └── extended_prompts.toml
```

#### **Using Shared Templates**
```toml
# In wikigen/specialized_prompts.toml
[[character_analysis.messages]]
role = "user"
content = """{% include '_common/base_instructions.jinja2' %}

Now analyze this character:
{{ character_data }}

{% include '_common/character_template.jinja2' %}"""
```

#### **Template Inheritance**
```jinja2
<!-- _common/base_article.jinja2 -->
# {{ article_title }}

{% block overview %}{% endblock %}

## History
{% block history %}{% endblock %}

## Relationships  
{% block relationships %}{% endblock %}
```

```toml
# Using inheritance
content = """{% extends '_common/base_article.jinja2' %}

{% block overview %}
{{ character_name }} is a {{ character_type }} who...
{% endblock %}

{% block history %}
Born in {{ birthplace }}, {{ character_name }}...
{% endblock %}"""
```

### **Prompt Manager Usage**

```python
# In agent code
from src.prompts import prompt_manager

class ArcSplitterAgent:
    async def analyze_story(self, story_title: str, story_content: str, ...):
        # 1. Get prompt group
        splitting_prompts = prompt_manager.get_group("wikigen.arc_splitting")
        
        # 2. Get message templates
        message_templates = splitting_prompts.get("messages")
        
        # 3. Render with context
        render_kwargs = {
            "story_title": story_title,
            "story_content": story_content,
            "total_chapters": len(chapters)
        }
        
        # 4. Build final messages
        final_messages = []
        for template in message_templates:
            rendered_content = splitting_prompts.render(
                template['content'], 
                **render_kwargs
            )
            final_messages.append(LLMMessage(
                role=template['role'], 
                content=rendered_content
            ))
        
        # 5. Make LLM call
        response = await self.llm_service.chat_completion(
            provider=provider,
            model=model,
            messages=final_messages,
            user_id=user_id
        )
        
        return response.content
```

---

## 🏗️ **Orchestrator Pattern**

### **Orchestrator Responsibilities**

The orchestrator is **NOT an agent** - it's a coordination layer that:

1. **Manages Agent Sequence**: Determines order of agent execution
2. **Handles Data Flow**: Passes outputs between agents
3. **Error Management**: Handles failures and retries
4. **State Management**: Tracks overall pipeline progress
5. **Resource Management**: Manages shared resources and cleanup

### **Orchestrator Structure**

```python
# wikigen/orchestrator.py
class WikiGenOrchestrator:
    """
    Orchestrates the complete WikiGen workflow.
    Manages all agents and coordinates the workflow.
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
        # Initialize all agents
        self.arc_splitter = ArcSplitterAgent(llm_service)
        self.summarizer = GeneralSummarizerAgent(llm_service)
        self.wiki_planner = WikiPlannerAgent(llm_service)
        self.article_writer = ArticleWriterAgent(llm_service)
        self.chapter_backlinker = ChapterBacklinkerAgent(llm_service)
    
    async def generate_wiki(
        self, 
        story: Story,
        user_id: UUID,
        provider: str,
        model: str
    ) -> WikiResult:
        """
        Main orchestration method that coordinates all agents.
        """
        try:
            # 1. Split story into arcs
            arcs = await self.arc_splitter.analyze_story(
                story_title=story.title,
                story_content=story.content,
                user_id=user_id,
                provider=provider,
                model=model
            )
            
            # 2. Process each arc
            wiki_archives = []
            previous_summaries = None
            
            for arc in arcs:
                # 3. Plan wiki structure
                wiki_plan = await self.wiki_planner.create_plan(
                    arc_content=arc.content,
                    mode="fresh" if arc.is_first else "update",
                    previous_summaries=previous_summaries,
                    user_id=user_id,
                    provider=provider,
                    model=model
                )
                
                # 4. Generate articles
                articles = await self.article_writer.write_articles(
                    wiki_plan=wiki_plan,
                    arc_content=arc.content,
                    mode="write" if arc.is_first else "update",
                    user_id=user_id,
                    provider=provider,
                    model=model
                )
                
                # 5. Create chapter backlinks
                enhanced_chapters = await self.chapter_backlinker.add_links(
                    chapters=arc.chapters,
                    wiki_articles=articles,
                    user_id=user_id,
                    provider=provider,
                    model=model
                )
                
                # 6. Save arc wiki archive
                arc_wiki = self._create_arc_archive(arc, articles, enhanced_chapters)
                wiki_archives.append(arc_wiki)
                
                # 7. Generate summaries for next arc
                previous_summaries = await self.summarizer.summarize_arc(
                    arc=arc,
                    articles=articles,
                    user_id=user_id,
                    provider=provider,
                    model=model
                )
            
            return WikiResult(
                archives=wiki_archives,
                total_arcs=len(arcs),
                processing_metadata=self._create_metadata()
            )
            
                 except Exception as e:
             logger.error(f"WikiGen orchestration failed: {e}")
             raise WikiGenError(f"Workflow execution failed: {e}")
    
    def _create_arc_archive(self, arc, articles, enhanced_chapters):
        """Helper method to package arc results"""
        pass
    
    def _create_metadata(self):
        """Helper method to create processing metadata"""
        pass
```

### **Orchestrator vs Agent Boundaries**

| Orchestrator | Agent |
|--------------|-------|
| ❌ Makes LLM calls | ✅ Makes LLM calls |
| ✅ Coordinates workflow | ❌ Knows about other agents |
| ✅ Manages state | ❌ Maintains state |
| ✅ Handles errors | ✅ Handles own errors |
| ✅ Data transformation | ✅ Data processing |
| ✅ Resource management | ❌ Resource management |

---

## 🔧 **Adding New Components**

### **Adding a New Agent**

1. **Create Agent File**
```python
# backend/src/agents/wikigen/new_agent.py
class NewAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def main_function(
        self,
        required_input: str,
        user_id: UUID,
        provider: str,
        model: str,
        optional_param: str = "default"
    ) -> AgentResult:
        """Main agent execution function"""
        pass
```

2. **Add Prompts to TOML**
```toml
[new_agent_section]
name = "New Agent Purpose"
description = "What this agent does"
version = "0.1"
author = "your_name"

[[new_agent_section.messages]]
role = "system"
content = """You are a specialized agent that..."""

[[new_agent_section.messages]]
role = "user"
content = """Process this input: {{ input_data }}"""
```

3. **Update Orchestrator**
```python
# In orchestrator.py
def __init__(self, llm_service: LLMService):
    # ... existing agents ...
    self.new_agent = NewAgent(llm_service)

async def generate_wiki(self, ...):
    # ... existing workflow ...
    new_result = await self.new_agent.main_function(...)
    # ... integrate result ...
```

4. **Add Tests**
```python
# tests/agents/wikigen/test_new_agent.py
import pytest
from src.agents.wikigen.new_agent import NewAgent

class TestNewAgent:
    async def test_main_function(self):
        # Test with mock LLM service
        pass
```

### **Adding a New Workflow**

1. **Create Workflow Directory**
```
backend/src/agents/new_workflow/
├── __init__.py
├── orchestrator.py
├── agent_one.py
├── agent_two.py
└── agent_three.py
```

2. **Create Prompt File**
```
backend/src/prompts/new_workflow.toml
```

3. **Implement Orchestrator**
```python
# new_workflow/orchestrator.py
class NewWorkflowOrchestrator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.agent_one = AgentOne(llm_service)
        self.agent_two = AgentTwo(llm_service)
        self.agent_three = AgentThree(llm_service)
    
    async def execute_workflow(self, ...):
        """Main workflow execution"""
        pass
```

### **Adding Shared Templates**

1. **Create Template File**
```jinja2
<!-- prompts/wikigen/_common/new_template.jinja2 -->
{% macro character_summary(character) %}
**{{ character.name }}** - {{ character.description }}
{% endmacro %}
```

2. **Use in Prompts**
```toml
[[section.messages]]
role = "user"
content = """{% from '_common/new_template.jinja2' import character_summary %}

Characters:
{% for char in characters %}
{{ character_summary(char) }}
{% endfor %}"""
```

---

## 🧪 **Testing Strategy**

### **Agent Testing**
```python
# Test individual agents in isolation
class TestArcSplitterAgent:
    @pytest.fixture
    def mock_llm_service(self):
        return MockLLMService()
    
    async def test_analyze_story(self, mock_llm_service):
        agent = ArcSplitterAgent(mock_llm_service)
        result = await agent.analyze_story(
            story_title="Test Story",
            story_content="Test content...",
            user_id=uuid4(),
            provider="openai",
            model="gpt-4"
        )
        assert result.arcs is not None
        assert len(result.arcs) > 0
```

### **Orchestrator Testing**
```python
# Test orchestrator with mock agents
class TestWikiGenOrchestrator:
    @pytest.fixture 
    def mock_agents(self):
        return {
            'arc_splitter': Mock(),
            'wiki_planner': Mock(), 
            'article_writer': Mock(),
            'chapter_backlinker': Mock()
        }
    
    async def test_generate_wiki_workflow(self, mock_agents):
        orchestrator = WikiGenOrchestrator(mock_llm_service)
        # Replace with mocks
        for name, mock_agent in mock_agents.items():
            setattr(orchestrator, name, mock_agent)
        
        # Test workflow
        result = await orchestrator.generate_wiki(test_story, ...)
        
        # Verify agent call sequence
        mock_agents['arc_splitter'].analyze_story.assert_called_once()
        mock_agents['wiki_planner'].create_plan.assert_called()
```

### **Prompt Testing**
```python
# Test prompt rendering
class TestPrompts:
    def test_arc_splitting_prompt_rendering(self):
        prompts = prompt_manager.get_group("wikigen.arc_splitting")
        rendered = prompts.render(
            "Analyze {{ story_title }}",
            story_title="Test Story"
        )
        assert "Test Story" in rendered
```

---

## 📊 **Best Practices**

### **Agent Development**
- ✅ Keep agents focused on single responsibilities
- ✅ Make all inputs explicit and typed
- ✅ Return structured, validated outputs  
- ✅ Handle errors gracefully with meaningful messages
- ✅ Add comprehensive logging
- ✅ Write unit tests for each agent

### **Prompt Management**
- ✅ Use descriptive section names
- ✅ Version your prompts
- ✅ Document template variables
- ✅ Test prompts with various inputs
- ✅ Use shared templates for common patterns
- ✅ Keep prompts maintainable and readable

### **Orchestrator Design**
- ✅ Keep orchestrators lightweight
- ✅ Handle errors at the right level
- ✅ Provide progress feedback
- ✅ Make workflows resumable when possible
- ✅ Log all major workflow steps
- ✅ Validate agent outputs before proceeding

### **Code Organization**
- ✅ Group related agents in workflow directories
- ✅ Use consistent naming conventions
- ✅ Keep shared utilities in common modules
- ✅ Document agent interfaces clearly
- ✅ Maintain separation between agents and orchestrators

This architecture provides a solid foundation for building complex, maintainable AI workflows while keeping individual components testable and reusable.
