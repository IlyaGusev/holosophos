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

Window 1:
```
uv run python -m academia_mcp --port 5056
```

Window 2:
```
uv run python -m mle_kit_mcp --port 5057 --workspace workdir
```

Window 3:
```
uv run python -m holosophos.server
```

Window 4:
```
uv run python -m codearkt.gradio
```

Go to http://127.0.0.1:7860/