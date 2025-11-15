# 🚀 5-Minute Ollama Setup for Slow Query Doctor

Get Ollama running locally in 5 minutes for private AI analysis of your database logs.

## Step 1: Install Ollama (2 minutes)

```bash
# macOS/Linux (one command)
curl -LsSf https://ollama.com/install.sh | sh

# Alternative: Download from https://ollama.com/download
```

## Step 2: Start Ollama & Pull Model (2 minutes)

```bash
# Start the Ollama server
ollama serve

# In a new terminal, pull a model
ollama pull llama2
```

## Step 3: Configure Slow Query Doctor (1 minute)

Create `.slowquerydoctor.yml` in your project:

```yaml
llm_provider: ollama
ollama_model: llama2
top_n: 5
output: reports/report.md
```

## Step 4: Test & Run

```bash
# Test Ollama setup
uv run python scripts/test_ollama.py

# Analyze your logs (no API key needed!)
uv run python -m slowquerydoctor your_postgresql.log
```

## ✅ Benefits

- **100% Private**: Your query data never leaves your machine
- **No API Costs**: Completely free to run
- **No Internet Required**: Works offline after model download
- **Enterprise Safe**: Perfect for sensitive production data

## Troubleshooting

**Model not found?**  
```bash
ollama list  # Check installed models
ollama pull llama2  # Pull if missing
```

**Connection refused?**  
```bash
ollama serve  # Make sure server is running
```

**Need different model?**  
```bash
ollama pull codellama  # For code-focused analysis
# Update .slowquerydoctor.yml: ollama_model: codellama
```

---

🎯 **Goal**: Your database logs analyzed by AI in minutes, completely private and free.