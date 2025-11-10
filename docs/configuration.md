# [← Back to Index](index.md)
# ⚙️ Configuration

For a summary, see the [Project README](../README.md#configuration).


## PostgreSQL Log Setup

See [Setup & Usage Examples](examples.md) for complete instructions on enabling slow query logging in PostgreSQL.


## Configuration File (.slowquerydoctor.yml)


You can create a `.slowquerydoctor.yml` file in your project directory to customize analysis options. Example:

```yaml
log_format: csv
min_duration: 1000
output: my_report.md
top_n: 10
llm_provider: openai  # or 'ollama'
openai_model: gpt-4o-mini
ollama_model: llama2
```


Set `llm_provider` to `openai` or `ollama` to choose which LLM backend to use. Specify the model for each provider with `openai_model` or `ollama_model`.

### Choosing Your LLM Provider: OpenAI vs Ollama

| Provider | Cost         | Privacy         | Speed         | Notes |
|----------|--------------|----------------|--------------|-------|
ollama_host: http://localhost:11434 # optional; override default Ollama host
llm_temperature: 0.3
max_tokens: 300
llm_timeout: 30
| OpenAI   | Paid (API)   | Data sent to OpenAI servers | Fast (cloud) | Requires API key, best for latest models |
| Ollama   | Free/local   | Data stays on your machine | Fast (local, depends on hardware) | Requires local install, limited to available models |
Set `llm_provider` to `openai` or `ollama` to choose which LLM backend to use. Specify the model for each provider with `openai_model` or `ollama_model`. Use `openai_api_key` or the `OPENAI_API_KEY` environment variable for OpenAI access, and `ollama_host` if your Ollama server runs on a non-default host.
- **OpenAI**: Use for access to the latest GPT models, high reliability, and cloud scalability. Requires an API key and incurs usage costs. Data is processed on OpenAI's servers.
- **Ollama**: Use for privacy, cost savings, and offline/local inference. No API key needed, but you must install Ollama and download models. Data never leaves your machine.

You can switch providers by changing `llm_provider` in your config file. For most users, OpenAI is best for accuracy and features; Ollama is best for privacy and cost.

See the README and this file for all available options.

## Environment Variables

| Variable           | Description                | Default           |
|--------------------|---------------------------|-------------------|
| OPENAI_API_KEY     | OpenAI API key (required) | None              |
| OPENAI_MODEL       | GPT model to use          | gpt-4o-mini       |
| OPENAI_BASE_URL    | Custom OpenAI endpoint    | Default API URL   |
| OLLAMA_HOST        | Custom Ollama host URL    | http://localhost:11434 |

## Dependencies

- `pyyaml` is required for config file support
- `pandas` and `tqdm` are required for multi-format log parsing and progress bars
