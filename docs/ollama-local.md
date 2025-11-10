# Running Ollama Locally

Ollama lets you run large language models on your own machine. To use it with this project, follow these steps:

## 1. Install Ollama
- Visit https://ollama.com/download and download the installer for your OS (macOS, Linux, Windows).
- Follow the installation instructions for your platform.

## 2. Start the Ollama Server
- After installation, start the Ollama server:
  - On macOS: Open Terminal and run:
    ```sh
    ollama serve
    ```
  - On Linux/Windows: Use the provided launcher or run the same command in your shell.

## 3. Pull a Model
- Before you can use a model, you need to download it. For example, to use Llama 2:
    ```sh
    ollama pull llama2
    ```
- You can find other models at https://ollama.com/library

## 4. Test the Server
- You can test the server with:
    ```sh
    ollama run llama2
    ```
- Or use the Python client as shown in `scripts/test_ollama.py`.

## 5. Troubleshooting
- If you get a `model not found` error, make sure you have pulled the model.
- The default server runs at `http://localhost:11434`.
- To make Slow Query Doctor use Ollama, set `llm_provider: ollama` in `.slowquerydoctor.yml`. If your Ollama server runs on a different host/port, add `ollama_host: http://your-host:port` to the config.

---
For more details, see the official docs: https://ollama.com/docs
