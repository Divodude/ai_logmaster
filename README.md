# AI LogMaster

**Smart error analysis tool with AI-powered solutions and dynamic documentation retrieval**

Wrap any command and get instant, intelligent debugging help powered by AI, dynamic documentation fetching, and pattern-based caching.

[![PyPI version](https://img.shields.io/pypi/v/ai-logmaster.svg)](https://pypi.org/project/ai-logmaster/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses LangChain and LLMs for intelligent error diagnosis
- 🎛️ **Visual Config Dashboard** - Beautiful web UI to configure everything — no file editing!
- ⚡ **Test Connection** - Validate your API key and model before you start
- 📚 **Dynamic Documentation Retrieval** - Automatically fetches relevant docs based on actual errors
- 🎯 **Smart Library Detection** - Identifies 20+ frameworks/libraries automatically
- 💰 **API Quota Optimization** - Intelligent agent minimizes API calls (70-80% reduction)
- 🔧 **Multi-Provider Support** - Works with Groq, OpenAI, Anthropic, Google, NVIDIA
- 🎨 **Class-Based Architecture** - Clean, modular, and easily extensible
- ⚙️ **JSON Configuration** - Customize error solutions and library keywords without code changes

## 🚀 Installation

```bash
pip install ai-logmaster
```

Or install from source:

```bash
git clone https://github.com/Divodude/ai-logmaster.git
cd ai-logmaster
pip install -e .
```

## 📖 Quick Start

### 1. Initialize Configuration

```bash
logmaster init
```

This opens a **beautiful configuration dashboard** in your browser where you can:

- 🤖 **Select your AI provider** — Groq, OpenAI, Anthropic, Google, or NVIDIA
- 🔑 **Enter your API key** — with show/hide toggle
- 🧪 **Test Connection** — validates your key, model, and provider with a real API call
- 🎛️ **Adjust temperature & max tokens** — with a live slider
- 🧠 **Toggle agent features** — cached solutions, doc fetching, auto-fix
- 📚 **Configure documentation search** — enable/disable web doc lookup
- 📟 **Set output verbosity** — control what gets logged to your terminal

Click **Save** and you're done — zero file editing required!

> **Note:** You can also set your API key via environment variable:
> ```bash
> export GROQ_API_KEY="your-api-key"
> ```

### 2. Run Your Command

```bash
logmaster run "python your_script.py"
```

That's it! The tool will:
1. ✅ Execute your command
2. ✅ Capture output in real-time
3. ✅ Detect errors automatically
4. ✅ Analyze with AI and dynamic documentation
5. ✅ Show solutions with relevant fixes

### 3. Auto-Fix Mode

```bash
logmaster run "python your_script.py" --auto-fix
```

AI will attempt to automatically fix detected errors in your code!

## 📋 Example Output

```
[TRIAGE] Executing: python broken.py
============================================================
[ERROR]  TypeError: unsupported operand type(s) for /: 'int' and 'str'
============================================================

[TRIAGE] ⚠️  Error detected! Analyzing...

[AGENT] Classifying error type...
[AGENT] Error type: type, Needs docs: True
[AGENT] Detected library: python
[AGENT] Fetching documentation from web...
[AGENT] ✓ Fetched 1847 chars of documentation
[AGENT] Analyzing with AI...
[AGENT] ✓ Analysis complete (API calls: 1)

╔══════════════════════════════════════════════════════════╗
║ 🔍 DIAGNOSIS                                             ║
╠══════════════════════════════════════════════════════════╣
║ Type: TypeError                                          ║
║ Confidence: 90%                                          ║
║ Method: AI + Docs                                        ║
╠══════════════════════════════════════════════════════════╣
║ 📋 ROOT CAUSE                                            ║
╠══════════════════════════════════════════════════════════╣
║ Division operation between integer and string           ║
╠══════════════════════════════════════════════════════════╣
║ 💡 RECOMMENDED FIXES                                     ║
╠══════════════════════════════════════════════════════════╣
║ 1. Ensure divisor is numeric type                       ║
║ 2. Convert string to int/float if needed                ║
║ 3. Validate inputs before operations                    ║
╚══════════════════════════════════════════════════════════╝
```

## 🏗️ Architecture

AI LogMaster uses a clean, modular class-based architecture:

### Core Components

```
ai_logmaster/
├── core/
│   ├── classifier.py          # ErrorClassifier - Pattern matching
│   ├── doc_fetcher.py         # DocumentationFetcher - Dynamic docs
│   ├── llm_client.py          # LLMClient - AI interactions
│   ├── llm_manager.py         # GlobalLLMManager - Provider routing
│   ├── agent.py               # Agent - LangGraph workflow
│   ├── analyzer.py            # ErrorAnalyzer - Main orchestrator
│   └── auto_fixer.py          # AutoFixer - AI code fixes
├── config/
│   ├── config.json            # Default configuration
│   ├── cached_solutions.json  # Error patterns & solutions
│   └── library_keywords.json  # Library detection keywords
├── dashboard/
│   ├── server.py              # Local HTTP server (stdlib)
│   ├── index.html             # Config dashboard UI
│   ├── style.css              # Dark-theme styling
│   └── script.js              # Dashboard logic
├── cli.py                     # Command-line interface
└── __init__.py
```

### How It Works

```
Error Detected
    ↓
ErrorClassifier (Pattern Matching - FREE)
    ↓
    ├─→ Common Error? → Cached Solution (0 API calls) ✅
    │
    └─→ Complex Error? → DocumentationFetcher (FREE)
                            ↓
                         Detect Library (FastAPI, Django, etc.)
                            ↓
                         Fetch Relevant Docs (DuckDuckGo)
                            ↓
                         LLMClient Analysis (1 API call) 💰
```

## ⚙️ Configuration

### Visual Dashboard (Recommended)

```bash
logmaster init
```

Opens a local web dashboard — configure everything visually and test your connection before saving.

### Supported AI Providers

| Provider | Models | Env Variable |
|----------|--------|-------------|
| **Groq** | llama-3.3-70b-versatile, mixtral-8x7b-32768 | `GROQ_API_KEY` |
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | `OPENAI_API_KEY` |
| **Anthropic** | claude-sonnet-4, claude-3-haiku | `ANTHROPIC_API_KEY` |
| **Google** | gemini-2.5-flash, gemini-2.5-pro | `GOOGLE_API_KEY` |
| **NVIDIA** | meta/llama-3.1-405b-instruct | `NVIDIA_API_KEY` |

### Manual Configuration

Config is stored at `~/.ai-logmaster/config.json`:

```json
{
  "ai": {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "api_key": "your-api-key",
    "temperature": 0.2,
    "max_tokens": 1000
  },
  "agent": {
    "use_cached_solutions": true,
    "fetch_documentation": true,
    "use_ai_analysis": true,
    "auto_fix": true
  },
  "documentation": {
    "enable_search": true,
    "search_engine": "duckduckgo"
  },
  "output": {
    "verbose": true,
    "show_api_calls": true
  }
}
```

### Customizing Error Solutions

Edit `ai_logmaster/config/cached_solutions.json` to add or modify error patterns and solutions:

```json
{
  "error_patterns": {
    "your_error": ["YourError", "your error message"]
  },
  "cached_solutions": {
    "your_error": {
      "type": "Your Error Type",
      "cause": "Root cause explanation",
      "fixes": ["Fix 1", "Fix 2", "Fix 3"],
      "confidence": 0.80,
      "method": "Cached"
    }
  }
}
```

### Customizing Library Detection

Edit `ai_logmaster/config/library_keywords.json` to add new libraries:

```json
{
  "libraries": {
    "your_library": {
      "keywords": ["your_lib", "yourlib"],
      "description": "Your library description"
    }
  }
}
```

**Supported Libraries (20+):**
FastAPI, Django, Flask, Requests, NumPy, Pandas, TensorFlow, PyTorch, SQLAlchemy, Asyncio, LangChain, OpenAI, Scikit-learn, Matplotlib, Selenium, BeautifulSoup, Pytest, Pydantic, Celery, Redis

## 💻 Programmatic Usage

### Class-Based API

```python
from ai_logmaster import ErrorAnalyzer

# Create analyzer
analyzer = ErrorAnalyzer()

# Analyze error
error_context = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = 10 / "invalid"
TypeError: unsupported operand type(s) for /: 'int' and 'str'
"""

result = analyzer.analyze(error_context)

print(f"Type: {result['type']}")
print(f"Cause: {result['cause']}")
print(f"Fixes: {result['fixes']}")
print(f"API Calls: {result.get('api_calls_used', 0)}")
```

### Using Individual Components

```python
from ai_logmaster.core import ErrorClassifier, DocumentationFetcher

# Use classifier standalone
classifier = ErrorClassifier()
error_type, needs_docs = classifier.classify(context)

# Use doc fetcher standalone
doc_fetcher = DocumentationFetcher()
library = doc_fetcher.detect_library("from fastapi import FastAPI")
# Returns: "fastapi"
```

### Backward Compatible API

```python
from ai_logmaster import analyze_error

# Still works!
result = analyze_error(error_context)
```

## 📊 API Call Optimization

**Without Agent**: Every error = 1 API call

**With Agent**:
- Connection errors: **0 API calls** ✅
- Import errors: **0 API calls** ✅
- Memory errors: **0 API calls** ✅
- Timeout errors: **0 API calls** ✅
- Permission errors: **0 API calls** ✅
- Syntax errors: 1 API call 💰
- Type errors: 1 API call 💰
- Unknown errors: 1 API call 💰

**Result**: 70-80% reduction in API calls!

## 🎯 Usage Examples

### Python Script
```bash
logmaster run "python app.py"
```

### Node.js Application
```bash
logmaster run "node server.js"
```

### Shell Script
```bash
logmaster run "bash deploy.sh"
```

### Complex Command
```bash
logmaster run "npm run build && npm start"
```

### With Custom Buffer Size
```bash
logmaster run "python script.py" --buffer 200
```

### With Auto-Fix
```bash
logmaster run "python script.py" --auto-fix
```

## 🧪 Development

### Install from Source

```bash
git clone https://github.com/Divodude/ai-logmaster.git
cd ai-logmaster
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all unit tests
python -m unittest discover -s tests
```

## 📦 Requirements

- Python 3.8+
- API key for your chosen AI provider (Groq, OpenAI, Anthropic, Google, or NVIDIA)

### Dependencies

```
langchain>=1.0.0
langchain-community>=0.4.0
langchain-core>=1.2.0
langchain-openai>=1.0.0
langgraph>=1.0.0
duckduckgo-search>=8.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.32.0
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 💬 Support

- 📧 Email: ry604492@gmail.com
- 🐛 Issues: https://github.com/Divodude/ai-logmaster/issues
- 📖 Docs: https://github.com/Divodude/ai-logmaster

## ☕ Buy Me a Coffee

If you find AI LogMaster helpful and want to support its development, consider buying me a coffee!

[buymeacoffee.com/divodude](https://buymeacoffee.com/divodude)

Every contribution, no matter how small, is greatly appreciated! 🙏

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - Documentation retrieval

## 🎯 What's New in v1.1.0

- 🎛️ **Visual Config Dashboard** — `logmaster init` now opens a beautiful web UI in your browser
- ⚡ **Test Connection** — validate your API key and model before saving
- 🤖 **Auto Model Suggestions** — dropdown suggestions based on your selected provider
- 🔐 **API Key Visibility Toggle** — show/hide your key in the dashboard
- 🎚️ **Temperature Slider** — fine-tune LLM creativity with a live slider
- 🧠 **Agent Feature Toggles** — enable/disable cached solutions, doc fetch, auto-fix
- 📦 **Zero Extra Dependencies** — dashboard uses Python's built-in HTTP server

### Previous: v1.0.1

- ✅ Class-Based Architecture
- ✅ Dynamic Documentation Fetching
- ✅ JSON Configuration
- ✅ 20+ Library Detection
- ✅ Auto-Fix Support

---

**Made with ❤️ by Divyansh**
