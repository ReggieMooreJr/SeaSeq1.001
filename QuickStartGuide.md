##Quick Start Guide##
#Execute DEMO 
./run.sh

# Execute the SEA SEQ Code 
./run-sea-seq.sh → build + run tests → generates reports.

# Build and start containers
./run-compose.sh → spin up API/DB/Web services and stream logs.

# View logs live
docker-compose logs -f --tail=100

# Stop containers
docker-compose down

# Stop + remove containers, networks, volumes
docker-compose down -v
