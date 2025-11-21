Perfect ✅ Here’s a **Quick Start README section** you can drop into your repo (`README.md` or `QuickStartGuide.md`) so users know exactly how to install and run the CLI.

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
   pip3 install questionary rich PyPDF2 python-dotenv requests
   ```

   *(Optional, for high-fidelity PDF parsing)*

   ```bash
   pip3 install pdfminer.six
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

| Option      | Description                     | Required |
| ----------- | ------------------------------- | -------- |
| `--input`   | Path to input file (CSV or PDF) | ✅        |
| `--api-url` | Sea-Seq API endpoint URL        | ✅        |
| `--api-key` | API key for authentication      | ✅        |

---

## 🖥️ Interactive Mode

If you run the CLI with no arguments, it will prompt you step-by-step (thanks to [questionary](https://github.com/tmbo/questionary)):

```bash
./seaseq_cli.py
```

Example prompts:

```
? Select input file: reports/issues.csv
? Enter API URL: https://seaseq.internal/api
? Enter API Key: ********
```

---

## ✅ Example

```bash
./seaseq_cli.py \
  --input ./reports/issues.csv \
  --api-url https://seaseq.internal/api \
  --api-key abc123XYZ
```

---

## 📝 Notes

* Ensure your `input` file follows the expected schema (see `templates/issues_template.csv`).
* API key must be active and authorized for the given endpoint.

---


