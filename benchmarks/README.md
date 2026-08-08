# 📊 AI LogMaster — Local LLM Benchmark Leaderboard

This repository tracks benchmarks and compatibility results for running **AI LogMaster** with **Local LLMs** (using Ollama, LM Studio, vLLM, Jan, KoboldCpp, etc.).

If you test AI LogMaster with local models, please submit your benchmark results to help the community discover optimal models and hardware configurations for local debugging!

---

## 🏆 Benchmark Leaderboard

| Model | Quantization | Runtime | Hardware | Diagnosis Quality | Auto-Fix | Avg Speed | Contributor | Details |
|---|---|---|---|---|---|---|---|---|
| *llama-3.2-3b-instruct* | Q4_K_M | Ollama | Apple M2 (16GB) | ⭐⭐⭐⭐☆ (4/5) | 🟢 Works | ~32 t/s | [@Divodude](https://github.com/Divodude) | [View Report](results/ollama-llama-3.2-3b.md) |
| *qwen2.5-coder-7b-instruct* | Q4_K_M | LM Studio | RTX 3060 12GB | ⭐⭐⭐⭐⭐ (5/5) | 🟢 Works | ~45 t/s | [@Divodude](https://github.com/Divodude) | [View Report](results/lmstudio-qwen2.5-coder-7b.md) |
| *mistral-7b-instruct-v0.3* | Q5_K_M | Ollama | Ryzen 7 5700X + RTX 4070 | ⭐⭐⭐⭐☆ (4/5) | 🟡 Partial | ~60 t/s | [@Divodude](https://github.com/Divodude) | [View Report](results/ollama-mistral-7b.md) |

> *Ratings:*
> - **Diagnosis Quality**: ⭐1-5 based on root cause accuracy and solution clarity.
> - **Auto-Fix**: 🟢 Fully Working | 🟡 Partial/Needs Edit | 🔴 Failed/Syntax Error.

---

## 🧪 How to Benchmark AI LogMaster Locally

### 1. Set Up Local Server
Start your local LLM server using an OpenAI-compatible endpoint:

- **Ollama**:
  ```bash
  ollama run llama3.2
  # Serves automatically at http://localhost:11434/v1
  ```
- **LM Studio**:
  - Load model -> Go to "Local Server" tab -> Start Server (`http://localhost:1234/v1`).

### 2. Configure AI LogMaster
Use the visual dashboard or edit `~/.ai-logmaster/config.json`:

```bash
logmaster init
```
In the dashboard:
- **Provider**: Select `OpenAI-Compatible` (or `Local / Custom`)
- **Base URL**: `http://localhost:11434/v1` (for Ollama) or `http://localhost:1234/v1` (for LM Studio)
- **Model Name**: e.g., `llama3.2` or `qwen2.5-coder-7b-instruct`

### 3. Run Test Commands
Run standard commands with standard errors and test auto-fix:

```bash
# Test basic error diagnosis
logmaster run "python -c 'import non_existent_package'"

# Test type error & auto-fix
logmaster run "python broken_script.py" --auto-fix
```

---

## 📤 How to Submit Your Benchmark

We welcome contributions from everyone! You can contribute in two easy ways:

### Method A: Pull Request (Recommended)
1. Copy `benchmarks/TEMPLATE.md` to `benchmarks/results/<runtime>-<model-name>.md`.
2. Fill in your benchmark details.
3. Add a row to the **Leaderboard Table** in `benchmarks/README.md`.
4. Submit a Pull Request titled `docs: add benchmark for <model-name> (<runtime>)`.

### Method B: GitHub Issue / Discussion
1. Open a new issue titled `[Benchmark] <Model Name> on <Runtime>`.
2. Copy the template from [`benchmarks/TEMPLATE.md`](TEMPLATE.md) into the issue description and fill it out.
3. A maintainer will verify and add it to the leaderboard!
