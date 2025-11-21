FROM python:3.12-slim

# Install system deps + Go
RUN apt-get update && apt-get install -y golang wget curl git && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Build SEA-SEQ Go CLI (if Go code exists)
RUN if [ -f cmd/sea-qa/main.go ]; then go build -o seaseq ./cmd/sea-qa; fi

# Expose ports for API and dashboard
EXPOSE 8000
EXPOSE 7107
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["bash", "run-sea-seq.sh"]
# The run-sea-seq.sh script should handle starting the API and dashboard services.

# Example content of run-sea-seq.sh:
# #!/bin/bash
# # Start the API server
# python api_server.py &
# # Start the dashboard server
# python dashboard_server.py &
# # Wait indefinitely to keep the container running
# tail -f /dev/null

# Make sure the script is executable
RUN chmod +x run-sea-seq.sh
# Note: Ensure that api_server.py and dashboard_server.py are the actual entry points for your services.
# Adjust the script and entry points as necessary for your application.