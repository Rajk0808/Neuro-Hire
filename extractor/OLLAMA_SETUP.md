# Setting Up Ollama for Local LLM Extraction

## Installation

### 1. Install Ollama
Download from: https://ollama.ai

Or install via package managers:
- **Windows (using Chocolatey)**: `choco install ollama`
- **macOS**: `brew install ollama`
- **Linux**: Visit https://ollama.ai/download

### 2. Start Ollama Server
```bash
ollama serve
```
This starts the server at `http://localhost:11434`

### 3. Download a Model
In a new terminal:
```bash
# Recommended: Mistral (7B, fast and accurate)
ollama pull mistral

# Or try these alternatives:
ollama pull llama2          # Larger, more capable
ollama pull neural-chat     # Good for conversation
ollama pull openchat        # Fast lightweight
```

### 4. Verify Installation
```bash
ollama list
```

### 5. Install Python Package
```bash
pip install ollama
```

## Usage

The app will automatically detect and use Ollama when available:

```bash
python run.py --mode hybrid
```

- If Ollama is running: Uses local LLM for enhanced extraction
- If Ollama is offline: Falls back to regex + spaCy NER extraction
- No API keys needed!

## Models

Recommended models for resume parsing:
- **mistral** (7B) - Best balance of speed/quality (default)
- **llama2** (7B) - More capable, slightly slower
- **neural-chat** (7B) - Good for instructions
- **openchat** (3.5B) - Fast, lightweight

Use `ollama pull <model>` to download, then edit the model name in `llm_extractor.py:extract_with_llm()`

## Troubleshooting

**"Ollama not available at localhost:11434"**
- Make sure `ollama serve` is running in another terminal
- Check: `curl http://localhost:11434/api/tags`

**Model not found**
- Run `ollama pull mistral` (or your chosen model)
- List available: `ollama list`

**Performance too slow**
- Use a smaller model: `ollama pull openchat`
- GPU acceleration: Set `OLLAMA_GPU=1` or install CUDA drivers

**Memory issues**
- Use a smaller model (3B instead of 7B)
- Or keep using regex+NER fallback (works great!)
