# AI LogMaster

**Smart error analysis tool with AI-powered solutions and dynamic documentation retrieval**

Wrap any command and get instant, intelligent debugging help powered by AI, dynamic documentation fetching, and pattern-based caching.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses LangChain and LLMs for intelligent error diagnosis
- 📚 **Dynamic Documentation Retrieval** - Automatically fetches relevant docs based on actual errors
- 🎯 **Smart Library Detection** - Identifies 20+ frameworks/libraries automatically
- 💰 **API Quota Optimization** - Intelligent agent minimizes API calls (70-80% reduction)
- ⚡ **Zero Setup** - Just wrap your command and go
- 🔧 **Multi-Provider Support** - Works with OpenAI, Anthropic, Google, NVIDIA, and more
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

This creates `~/.ai-logmaster/config.yaml`. Edit it to set your API key:

```yaml
ai:
  provider: "nvidia"
  api_key: "your-api-key-here"
```

Or use environment variable:
```bash
export NVIDIA_API_KEY="your-api-key"
```

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
[AGENT] Search 1/2: python unsupported operand type(s)...
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
│   ├── agent.py               # Agent - LangGraph workflow
│   └── analyzer.py            # ErrorAnalyzer - Main orchestrator
├── config/
│   ├── cached_solutions.json  # Error patterns & solutions
│   └── library_keywords.json  # Library detection keywords
└── cli.py                     # Command-line interface
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

### AI Providers

Edit `~/.ai-logmaster/config.yaml`:

#### NVIDIA (Default - Free Tier Available)
```yaml
ai:
  provider: "nvidia"
  model: "mistralai/mistral-small-3.1-24b-instruct-2503"
  api_key: "${NVIDIA_API_KEY}"
  base_url: "https://integrate.api.nvidia.com/v1"
```

#### OpenAI
```yaml
ai:
  provider: "openai"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
```

#### Anthropic
```yaml
ai:
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  api_key: "${ANTHROPIC_API_KEY}"
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

### API Optimization

```yaml
agent:
  use_cached_solutions: true  # Use cached solutions for common errors
  fetch_documentation: true   # Fetch docs from web
  
  # These errors use cached solutions (0 API calls)
  cached_error_types:
    - connection
    - import
    - memory
    - timeout
    - permission
  
  # These errors use AI + docs (1 API call each)
  complex_error_types:
    - syntax
    - type
    - value
    - unknown
```

### Quota Management

```yaml
quota:
  enabled: true
  daily_limit: 100      # Maximum API calls per day
  warn_threshold: 0.8   # Warn at 80%
```

## 💻 Programmatic Usage

### Class-Based API (New)

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

## 🧪 Development

### Install from Source

```bash
git clone https://github.com/Divodude/ai-logmaster.git
cd ai-logmaster
pip install -e .
```

### Run Tests

```bash
# Test class architecture
python test_class_architecture.py

# Test library detection
python test_library_keywords.py

# Test agent workflow
python run_agent_tests.py
```

### Project Structure

```
ai-logmaster/
├── ai_logmaster/
│   ├── core/                   # Core modules
│   │   ├── classifier.py       # Error classification
│   │   ├── doc_fetcher.py      # Documentation fetching
│   │   ├── llm_client.py       # LLM interactions
│   │   ├── agent.py            # LangGraph agent
│   │   └── analyzer.py         # Main analyzer
│   ├── config/                 # Configuration
│   │   ├── cached_solutions.json
│   │   ├── library_keywords.json
│   │   └── config.yaml.example
│   ├── cli.py                  # CLI interface
│   └── __init__.py
├── tests/                      # Test files
├── setup.py
├── requirements.txt
└── README.md
```

## 📦 Requirements

- Python 3.8+
- API key for your chosen AI provider (NVIDIA, OpenAI, Anthropic, or Google)

### Dependencies

```
langchain-openai
langchain-community
langchain-core
langgraph
duckduckgo-search
python-dotenv
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

<div align="center">
  <img src="upi_qr.png" alt="UPI QR Code" width="300"/>
  <p><em>Scan to send ₹100 via UPI</em></p>
</div>

Every contribution, no matter how small, is greatly appreciated! 🙏

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - Documentation retrieval

## 🎯 Key Improvements in v1.0.1

- ✅ **Class-Based Architecture** - Clean, modular, and extensible
- ✅ **Dynamic Documentation** - Fetches docs based on actual errors
- ✅ **JSON Configuration** - Customize without code changes
- ✅ **20+ Library Detection** - Automatic framework identification
- ✅ **Better Error Analysis** - Improved accuracy with context-aware docs
- ✅ **Fallback Support** - Graceful degradation if configs missing

---

**Made with ❤️ by Divyansh**
