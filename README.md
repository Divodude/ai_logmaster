# AI LogMaster

**Smart error analysis tool with AI-powered solutions**

Wrap any command and get instant, intelligent debugging help powered by AI and documentation retrieval.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🤖 **AI-Powered Analysis** - Uses LangChain and LLMs for intelligent error diagnosis
- 📚 **Smart Documentation Retrieval** - Automatically fetches relevant docs when needed
- 💰 **API Quota Optimization** - Intelligent agent minimizes API calls (70-80% reduction)
- ⚡ **Zero Setup** - Just wrap your command and go
- 🔧 **Multi-Provider Support** - Works with OpenAI, Anthropic, Google, NVIDIA, and more
- 🎯 **Pattern-Based Caching** - Common errors use cached solutions (no API calls)

## Installation

```bash
pip install ai-logmaster
```

## Quick Start

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
4. ✅ Analyze with AI
5. ✅ Show solutions with documentation references

## Example Output

```
[TRIAGE] Executing: python broken.py
============================================================
[ERROR]  TypeError: unsupported operand type(s) for /: 'int' and 'str'
============================================================

[TRIAGE] ⚠️  Error detected! Analyzing...

[AGENT] Classifying error type...
[AGENT] Error type: type, Needs docs: True
[AGENT] Fetching documentation from web...
[AGENT] ✓ Fetched 989 chars of documentation
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
╠══════════════════════════════════════════════════════════╣
║ 📚 DOCUMENTATION SOURCES                                 ║
╠══════════════════════════════════════════════════════════╣
║ • https://docs.python.org/3/library/exceptions.html     ║
╚══════════════════════════════════════════════════════════╝
```

## Configuration

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

#### Google
```yaml
ai:
  provider: "google"
  model: "gemini-pro"
  api_key: "${GOOGLE_API_KEY}"
```

### Agent Optimization

Control when AI is used to minimize API costs:

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

## How It Works

### Smart Agent Flow

```
Error Detected
    ↓
Classify Error (Pattern Matching - FREE)
    ↓
    ├─→ Common Error? → Use Cached Solution (0 API calls)
    │
    └─→ Complex/Unknown? → Fetch Docs (FREE) → AI Analysis (1 API call)
```

### API Call Optimization

**Without Agent**: Every error = 1 API call

**With Agent**:
- Connection errors: 0 API calls ✅
- Import errors: 0 API calls ✅
- Memory errors: 0 API calls ✅
- Timeout errors: 0 API calls ✅
- Permission errors: 0 API calls ✅
- Syntax errors: 1 API call 💰
- Type errors: 1 API call 💰
- Unknown errors: 1 API call 💰

**Result**: 70-80% reduction in API calls!

## Usage Examples

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

## Advanced Features

### RAG Support (Optional)

Install with RAG capabilities for enhanced documentation retrieval:

```bash
pip install ai-logmaster[rag]
```

Enable in config:
```yaml
rag:
  enabled: true
  vector_store: "faiss"
  chunk_size: 1000
  top_k: 3
```

## Development

### Install from Source

```bash
git clone https://github.com/Divodude/ai-logmaster.git
cd ai-logmaster
pip install -e .
```

### Run Tests

```bash
python run_agent_tests.py
```

## Requirements

- Python 3.8+
- API key for your chosen AI provider (NVIDIA, OpenAI, Anthropic, or Google)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

- 📧 Email: ry604492@gmail.com
- 🐛 Issues: https://github.com/Divodude/ai-logmaster/issues
- 📖 Docs: https://github.com/Divodude/ai-logmaster

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - Documentation retrieval

---

**Made with ❤️ by Divyansh**
