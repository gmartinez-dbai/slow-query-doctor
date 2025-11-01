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
openai_model: gpt-4o-mini
```

See the README and this file for all available options.

## Environment Variables

| Variable           | Description                | Default           |
|--------------------|---------------------------|-------------------|
| OPENAI_API_KEY     | OpenAI API key (required) | None              |
| OPENAI_MODEL       | GPT model to use          | gpt-4o-mini       |
| OPENAI_BASE_URL    | Custom OpenAI endpoint    | Default API URL   |

## Dependencies

- `pyyaml` is required for config file support
- `pandas` and `tqdm` are required for multi-format log parsing and progress bars
