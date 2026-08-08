# Local LLM Benchmark Report

## 📌 Benchmark Overview

| Property | Details |
|---|---|
| **Model Name** | *(e.g. qwen2.5-coder-7b-instruct)* |
| **Model Size / Quantization** | *(e.g. 7B, Q4_K_M, 4-bit)* |
| **Runtime** | *(Ollama / LM Studio / vLLM / Jan / KoboldCpp / Other)* |
| **Runtime Version** | *(e.g. Ollama v0.5.1)* |
| **OS / Operating System** | *(Windows 11 / macOS Sonoma / Ubuntu 24.04)* |
| **Hardware Specs** | *(e.g. Apple M2 16GB / Ryzen 5600X + RTX 3060 12GB)* |
| **Submitted By** | *@username* |

---

## ⚡ Performance Summary

- **Diagnosis Accuracy**: ⭐⭐⭐⭐⭐ (x / 5 stars)
- **Auto-Fix Capability**: 🟢 Works / 🟡 Partial / 🔴 Fails
- **Average Speed / Latency**: *(e.g. ~40 tokens/sec, response in 2.1s)*
- **Memory / RAM Usage**: *(e.g. VRAM: 5.2GB, System RAM: 8GB)*

---

## 🧪 Test Results

### 1. Simple Error Diagnosis (Syntax / Import Error)
- **Status**: [ ] Passed  [ ] Failed
- **Quality of Diagnosis**: *(Brief description of how clear the explanation was)*
- **Response Time**: *(e.g. 1.2s)*

### 2. Complex Multi-Line Error Diagnosis (TypeError / Logic Error)
- **Status**: [ ] Passed  [ ] Failed
- **Quality of Diagnosis**: *(Did it accurately isolate the root cause?)*

### 3. Auto-Fix Code Generation (`--auto-fix`)
- **Status**: [ ] Passed  [ ] Partial  [ ] Failed
- **Code Fix Quality**: *(Did generated fix work directly without breaking format?)*

---

## 💡 Notes & Issues Encountered
- *(Any prompt formatting issues, context length limits, hallucinations, or system requirements worth noting?)*

---

## 🔧 Config snippet used
```json
{
  "ai": {
    "provider": "openai_compatible",
    "base_url": "http://localhost:11434/v1",
    "model": "qwen2.5-coder:7b",
    "temperature": 0.2
  }
}
```
