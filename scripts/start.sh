#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip

if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  pip install python-dotenv openai rank-bm25
fi

mkdir -p memory/logs data

python - <<'PY'
import sqlite3
from pathlib import Path
from tools.memory.memory_db import get_connection

Path('data').mkdir(exist_ok=True)

# Ensure memory schema is current and compatible with memory tools
conn = get_connection()
conn.close()

# Ensure activity DB schema exists
aconn = sqlite3.connect('data/activity.db')
aconn.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    source TEXT,
    request TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    summary TEXT
)''')
aconn.commit()
aconn.close()
PY

python tools/memory/memory_read.py --format summary

echo "Session ready ✅"
