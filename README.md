### Holosophos

Autonomous research assistant composed of specialized agents for literature discovery, experiment execution on remote GPUs, technical writing, idea generation, and paper review.

Built on top of:
- [CodeArkt agentic framework](https://github.com/IlyaGusev/codearkt)
- [Academia MCP server](https://github.com/IlyaGusev/academia_mcp)
- [MLE kit MCP server](https://github.com/IlyaGusev/mle_kit_mcp)


### Features
- **Manager agent**: Orchestrates task flow across specialized agents.
- **Librarian**: Searches papers (ArXiv, ACL Anthology, Semantic Scholar), reads webpages, and analyzes documents.
- **MLE Solver**: Writes and runs code on remote GPUs via MLE Kit MCP tools.
- **Writer**: Composes LaTeX reports/papers and compiles them to PDF.
- **Proposer**: Generates and scores research ideas given context and a baseline paper.
- **Reviewer**: Reviews papers with venue-grade criteria.

### Architecture at a glance
- Server entrypoint: `holosophos.server` (starts a CodeArkt server with the composed agent team)
- Agent composition: `holosophos.main_agent.compose_main_agent`
- Agent prompts: `holosophos/prompts/*.yaml`
- Settings: `holosophos/settings.py` (env-driven via `pydantic-settings`)
- External MCPs:
  - `academia_mcp` (papers/search)
  - `mle_kit_mcp` (remote GPU execution, file ops)
- Optional tracing/observability: Phoenix (OTLP)

### Requirements
- Python 3.12+
- Docker
- `uv` (recommended for fast Python environment management)

### Installation
```bash
uv venv .venv
source .venv/bin/activate
make install
```

### Environment configuration
Create a `.env` file at the project root. Typical entries:
```bash
# LLM provider keys (use what you need)
OPENROUTER_API_KEY=...

# Tooling keys
TAVILY_API_KEY=...
VAST_AI_KEY=...

# Optional observability
PHOENIX_URL=http://localhost:6006
PHOENIX_PROJECT_NAME=holosophos

# MCP endpoints when running locally
ACADEMIA_MCP_URL=http://0.0.0.0:5056/mcp
MLE_KIT_MCP_URL=http://0.0.0.0:5057/mcp

# App options
MODEL_NAME=deepseek/deepseek-chat-v3.1
PORT=5055
```

Holosophos reads configuration from `holosophos/settings.py`. You can override any setting via environment variables (case-insensitive), for example `MODEL_NAME`, `MAX_COMPLETION_TOKENS`, `ENABLE_PHOENIX=true`, or custom `PHOENIX_ENDPOINT`.

### Quickstart: Local (multi-process)
Open separate terminals and run:

1) Phoenix (optional, for traces)
```bash
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix
```

2) Academia MCP (papers)
```bash
uv run python -m academia_mcp --port 5056
```

3) MLE Kit MCP (GPU exec; with local workspace bind)
```bash
uv run python -m mle_kit_mcp --port 5057 --workspace workdir
```

4) Holosophos server
```bash
uv run python -m holosophos.server --port 5055 --enable-phoenix
```

5) Client UI (choose one)
```bash
# Gradio UI
uv run python -m codearkt.gradio

# Terminal client
uv run python -m codearkt.terminal
```

The server listens on `http://localhost:5055`. The manager agent will call into MCP tools from Academia and MLE Kit as needed.

### Quickstart: Docker Compose
Holosophos ships with a `docker-compose.yml` that brings up:
- `app` (Holosophos server)
- `executor` (CodeArkt executor)
- `phoenix` (optional tracing UI and OTLP collector)
- `academia` (Academia MCP)
- `mle_kit` (MLE Kit MCP, with `./workdir` mounted and Docker socket pass-through)

Steps:
```bash
# 1) Ensure you have a .env at project root (see above)
# 2) Start the stack
docker compose up --build
```

Default ports:
- App: `http://localhost:5055`
- Phoenix UI: `http://localhost:6006`
- Academia MCP: `http://localhost:5056`
- MLE Kit MCP: `http://localhost:5057`

You can change ports via environment variables in `docker-compose.yml` (`APP_PORT`, `PHOENIX_UI_PORT`, `PHOENIX_OTLP_PORT`, `ACADEMIA_PORT`, `MLE_KIT_PORT`).

#### Compose commands and tips
```bash
# Start everything in the background
docker compose up -d --build

# Tail logs for a service
docker compose logs -f app
docker compose logs -f phoenix
docker compose logs -f academia
docker compose logs -f mle_kit
docker compose logs -f executor

# Restart or rebuild a single service
docker compose restart app
docker compose build app --no-cache && docker compose up -d app

# Stop and remove (including named volumes, if any)
docker compose down -v
```

#### Override ports and options at runtime
```bash
# Example: change app and Phoenix UI ports for this run only
APP_PORT=8055 PHOENIX_UI_PORT=6606 docker compose up -d --build
```

#### Workspace and persistence
- `./workdir` is bind-mounted into both `academia` and `mle_kit` containers at `/workdir`.
- Use `workdir/` for inputs and outputs you want to inspect or edit from the host.
- The `mle_kit` service has `/var/run/docker.sock` mounted to orchestrate jobs; see the security note below.

#### Interacting with the stack
Run a client in a separate terminal to talk to the app at `http://localhost:${APP_PORT:-5055}`:
```bash
# Gradio UI
uv run python -m codearkt.gradio

# or terminal client
uv run python -m codearkt.terminal
```

#### Customizing the model and tracing
- Set `MODEL_NAME` in `.env` (or export it) to change the model (default comes from `holosophos/settings.py`).
- Enable tracing by setting `ENABLE_PHOENIX=true` and ensuring Phoenix is up. The app will send OTLP traces to `${PHOENIX_URL}/v1/traces` unless `PHOENIX_ENDPOINT` is provided.

#### Security note
Mounting `/var/run/docker.sock` into `mle_kit` grants it control over the host Docker daemon. Only run this stack on a trusted machine and network.

### Using the agents
The server composes a manager agent with five specialists:
- **librarian**: queries literature and the web (no file system access)
- **mle_solver**: executes code on remote GPUs (remote tools)
- **writer**: creates LaTeX PDFs (templates, compile)
- **proposer**: ideates and scores research proposals
- **reviewer**: reviews papers using venue-style rubrics

Prompts live under `holosophos/prompts/` and can be customized per agent (`*.yaml`). Tool sets and iteration limits are configured in `holosophos/settings.py` and can be overridden via environment variables.

### Development
- Install dev tools: `make install`
- Format: `make black`
- Lint & type-check: `make validate`
- Tests: `make test`

### Troubleshooting
- If the manager cannot reach MCP servers, verify `ACADEMIA_MCP_URL` and `MLE_KIT_MCP_URL` match the ports you started.
- For tracing, ensure Phoenix is running and `ENABLE_PHOENIX=true` (or pass `--enable-phoenix`).
- Ensure LLM credentials are present in `.env` for your chosen provider(s).
