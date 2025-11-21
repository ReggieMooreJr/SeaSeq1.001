USAGE.MD
# Sea-Seq CLI — Usage Guide

This document expands on the Quick Start and shows advanced usage patterns for the Sea-Seq CLI.

---

## 🔧 Basic Command

```bash
./seaseq_cli.py --input ./reports/issues.csv --api-url https://seaseq.internal/api --api-key YOUR_API_KEY



## 🔧 Best Practice 
Create an .env file that will already have the $API_URL and $API_KEY



## 🔧 Example with csv and pdf 
./seaseq_cli.py --input ./reports/issues.csv --api-url $API_URL --api-key $API_KEY


./seaseq_cli.py --input ./reports/security_audit.pdf --api-url $API_URL --api-key $API_KEY

🛠️ Error Handling

If your API key is wrong → you’ll see an Authentication Error

If your CSV is malformed → the CLI will highlight missing fields

If the server is unreachable → you’ll see a Connection Error

📊 Output

The CLI prints a styled report in your terminal (via rich
):

Number of issues found

Severity levels

Upload confirmation (success/failure)

It may also return a JSON response from the API for integration into pipelines.