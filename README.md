# Playground.test
Play ground for my vibe coding

## Start a session

```bash
./scripts/start.sh
```

If you're bootstrapping manually (without `scripts/start.sh`):

```bash
pip install python-dotenv openai rank-bm25 fastapi uvicorn
```

## Run tests

```bash
python -m unittest
```

## Run Jarvis proto v0

```bash
python jarvis.py "summarize repo readiness" --plan-only
python jarvis.py "run verification checks"
```

## Run Jarvis Gateway (web + websocket)

```bash
./scripts/start.sh
python -m jarvis.gateway
```

Then open:

```text
http://127.0.0.1:8787
```

Example websocket payload to `ws://127.0.0.1:8787/ws`:

```json
{
  "workspace": "default",
  "text": "Plan a repo verification run",
  "mode": "plan"
}
```
