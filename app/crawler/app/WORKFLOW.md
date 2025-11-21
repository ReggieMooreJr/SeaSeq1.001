# ✅ MCP Site Scanner — Summary of Workflow

A concise operational map for developers and operators.

---

## ⚙️ Command Table

| Action | Command | Description |
|--------|----------|-------------|
| **Start API server** | `make api` | Runs Flask API on port 8020 |
| **Run CLI scan** | `make cli` | Scans interactively and prints report location |
| **One-off scan** | `make once` | Scans once and exits with timing summary |
| **Run all tests** | `make test` | Executes cucumber + pytest |
| **Build Docker** | `make docker-build` | Builds image with dependencies |
| **Run Docker** | `make docker-run` | Launches container with /app/reports persisted |
| **Clean environment** | `make clean` | Removes all temporary artifacts |

---

## 🧭 Developer Workflow

1. **Local Setup**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
