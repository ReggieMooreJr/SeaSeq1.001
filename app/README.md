Got it ✅ — here’s the updated **README.md** with a note about the **Userguides folder** so contributors and users know where to find additional documentation.

---

# 🚀 Sea-Seq CLI — Quick Start Guide

The **Sea-Seq Validation CLI** helps you validate and upload issue reports to the Sea-Seq API.

---

## 📦 Requirements

* macOS / Linux / Windows (with Python 3.8+)
* Python 3
* `pip3` for installing dependencies

---

## 🔧 Installation

1. **Clone this repo** or download the release ZIP.

   ```bash
   git clone https://github.com/YOUR_ORG/SEA-SEQ_demo.git
   cd SEA-SEQ_demo
   ```

2. **Install dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Make the CLI executable (macOS/Linux only)**

   ```bash
   chmod +x seaseq_cli.py
   ```

---

## 🚀 Usage

### Option 1: Run directly with Python

```bash
python3 seaseq_cli.py --input ./reports/issues.csv --api-url https://seaseq.internal/api --api-key YOUR_API_KEY
```

### Option 2: Run as an executable

```bash
./seaseq_cli.py --input ./reports/issues.csv --api-url https://seaseq.internal/api --api-key YOUR_API_KEY
```

---

## 📌 Arguments

| Option      | Description                            | Required |
| ----------- | -------------------------------------- | -------- |
| `--input`   | Path to input file (.csv, .json, .pdf) | ✅        |
| `--api-url` | Sea-Seq API endpoint URL               | ✅        |
| `--api-key` | API key for authentication             | ✅        |
| `--export`  | Optional: Export parsed issues to JSON | ❌        |

---

## 🖥️ Interactive Mode

If you run the CLI with no arguments, it will prompt you step-by-step:

```bash
./seaseq_cli.py
```

---

## 📂 Additional Documentation

This repository includes several **detailed user guides** in the [`Userguides/`](Userguides) folder:

* **Quick Start** — how to get up and running
* **Usage** — advanced options and file formats
* **Examples** — demo files (`.csv`, `.json`, `.pdf`) you can try immediately
* **Runbook** — operational best practices

👉 Check the **Userguides folder** if you want more in-depth walkthroughs, examples, or troubleshooting help.

---

## ✅ Example

```bash
./seaseq_cli.py \
  --input ./demo/issues.json \
  --api-url https://seaseq.internal/api \
  --api-key abc123XYZ \
  --export parsed.json
######CLI vs API vs Runne#####```

👉 You need to choose which mode you want as default.

Option A — Default = Runner

If you want Docker to auto-generate a report when launched:

CMD ["python", "runner.py"]

Option B — Default = API (likely safer)

If you want the API as the default (current state), but sometimes run runner:

docker run --rm myimage python runner.py
---
## ✅ Test Reports rendering 

execute the following 

python3 test_render.py
🔹 How to use all three modes
🔹 Usage examples
#####################################
API (default)

docker run -d -p 8000:8000 sea-seq:latest


Run CLI via runner_cli.py

docker run --rm --entrypoint python sea-seq:latest runner_cli.py scan --target demo.com


Run Report generator directly

docker run --rm --entrypoint python sea-seq:latest runner_report.py

