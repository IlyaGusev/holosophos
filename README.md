# Holosophos

Tools and agents for autonomous research.

## Install

Dependencies:
```
uv venv .venv
source .venv/bin/activate
make install
```

Tokens in .env:
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
VAST_AI_KEY=...
```

Logging to HF:
```
huggingface-cli login
```


## Run

```
uv run python -m holosophos.main_agent --query "..." --model-name "anthropic/claude-3-5-sonnet-20241022"
```
