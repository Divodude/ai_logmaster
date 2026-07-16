# Ai Log Master - Workflow Diagram

This document contains the execution flow of the `Ai_log_master` application from the entry point down to error analysis and auto-fixing.

## Execution Flow

```mermaid
graph TD
    Start([User Runs CLI Command<br/>`logmaster run <cmd>`]) --> Triage[TriageWrapper<br/>Executes Command]
    Triage --> Monitor[Monitor Output<br/>in Real-time]
    
    Monitor --> CheckError{Error Keywords Detected?<br/>or Non-Zero Exit?}
    
    CheckError -- No --> Success([Command Successful<br/>Exit])
    
    CheckError -- Yes --> Capture[Capture Log Context<br/>Last 20 lines]
    Capture --> Analyzer[ErrorAnalyzer]
    
    Analyzer --> Ingestor[CodebaseIngestor<br/>Fetch related files/context]
    Ingestor --> AgentTry{Try LangGraph Agent}
    
    AgentTry -- Success --> Graph[LangGraph Workflow]
    
    subgraph LangGraph Agent
        Graph --> Classify[Classify Error Type]
        Classify --> NeedDocs{Needs Docs?}
        NeedDocs -- Yes --> FetchDocs[Fetch Docs from Web]
        NeedDocs -- No --> SkipDocs[Skip Fetching]
        FetchDocs --> AIAnalyze[AI Analysis<br/>with LLMClient]
        SkipDocs --> AIAnalyze
    end
    
    AgentTry -- Fails --> BasicAI[Fallback 1:<br/>Basic AI Analysis]
    BasicAI -- Fails --> Cached[Fallback 2:<br/>Cached/Generic Solution]
    
    AIAnalyze --> Results
    BasicAI -- Success --> Results
    Cached --> Results
    
    Results[Display Diagnosis & Fixes] --> AutoFixCheck{Auto-fix Flag Set<br/>or User Opt-in?}
    
    AutoFixCheck -- No --> End([End])
    
    AutoFixCheck -- Yes --> AutoFixer[AutoFixer]
    
    subgraph Auto Fixer Process
        AutoFixer --> Filter[Filter User Files]
        Filter --> LLMFix[LLM Generates Fix snippet]
        LLMFix --> Diff[Show Unified Diff]
        Diff --> Confirm{User Confirms?}
        Confirm -- Yes --> Patch[Apply Patch to File]
        Confirm -- No --> SkipPatch[Skip Fix]
    end
    
    Patch --> End
    SkipPatch --> End
```

## Key Components

1. **CLI (`cli.py`)**: The entry point which parses arguments and wraps the execution using `TriageWrapper`.
2. **TriageWrapper**: Streams terminal output and looks for error indicators (keywords or exit codes).
3. **ErrorAnalyzer (`core/analyzer.py`)**: The main orchestrator that manages the fallback chain (LangGraph Agent -> Basic AI -> Pattern Matching).
4. **Agent (`core/agent.py`)**: A LangGraph state machine that intelligently classifies the error, fetches relevant documentation from the web if necessary, and then invokes the LLM.
5. **CodebaseIngestor (`core/ingestor.py`)**: Parses the stack trace to fetch the user's local code files, providing the LLM with deeper context.
6. **AutoFixer (`core/auto_fixer.py`)**: Prompts the LLM to rewrite the faulty code block, generates a safe diff, and writes it back to disk upon user confirmation.
