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
TAVILY_API_KEY=...
```

Logging to HF:
```
huggingface-cli login
```


## Run

Window 1 (logs server):
```
docker container run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix
```

Window 2 (Academia MCP):
```
uv run python -m academia_mcp --port 5056
```

Window 3 (MLE kit MCP):
```
uv run python -m mle_kit_mcp --port 5057 --workspace workdir
```

Window 4 (Main server):
```
uv run python -m holosophos.server
```

Window 5 (Gradio or terminal):
```
uv run python -m codearkt.gradio
uv run python -m codearkt.terminal
```
