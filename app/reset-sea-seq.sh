#!/bin/bash
set -e  # Exit immediately if a command fails

# Step 1: If reports exist, archive them
if [ -d "./reports" ]; then
    echo "Archiving old reports..."
    
    # Ensure archive directory exists
    mkdir -p ./reports/archive
    
    # Use timestamp for unique folder
    timestamp=$(date +"%Y%m%d_%H%M%S")
    mkdir -p ./reports/archive/$timestamp
    
    # Move everything inside reports (ignore errors if empty)
    mv ./reports/* ./reports/archive/$timestamp/ 2>/dev/null || true
fi

# Step 2: Reset reports directory
mkdir -p ./reports
echo "Reports directory reset. Ready for new run!"
# Step 3: Optional - Clean up Docker containers and images
echo "Cleaning up Docker containers and images..."
# Stop and remove all containers
docker-compose down || docker rm -f $(docker ps -aq) 2>/dev/null || true
# Remove all images
docker rmi -f $(docker images -q) 2>/dev/null || true || true # Ignore errors if no images  exist       
echo "Docker cleanup complete." 
# Note: Uncomment the following lines if you want to remove volumes and networks as well
# docker volume rm $(docker volume ls -q) 2>/dev/null || true
# docker network rm $(docker network ls -q) 2>/dev/null || true
echo "Reset complete."
# End of script
# --- IGNORE ---