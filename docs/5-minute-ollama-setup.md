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

# In a new terminal, pull a model (specialized for SQL)
ollama pull arctic-text2sql-r1:7b
```

> **Why Arctic-Text2SQL-R1 7B?** This model is specifically fine-tuned for SQL tasks, making it ideal for database query analysis and optimization recommendations.

## Step 3: Configure Slow Query Doctor (1 minute)

Create `.slowquerydoctor.yml` in your project:

```yaml
llm_provider: ollama
ollama_model: arctic-text2sql-r1:7b
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
ollama pull arctic-text2sql-r1:7b  # Pull if missing
```

**Connection refused?**  
```bash
ollama serve  # Make sure server is running
```

**Need different model?**  
```bash
# Alternative SQL-focused models
ollama pull codellama     # General code analysis
ollama pull sqlcoder      # SQL-specific (if available)
ollama pull llama3.2        # General purpose fallback

# Update .slowquerydoctor.yml with your chosen model:
# ollama_model: your-model-name
```

---

🎯 **Goal**: Your database logs analyzed by AI in minutes, completely private and free.