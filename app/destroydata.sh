 #!/bin/bash

# Exit immediately if any command fails
set -e   

    docker compose run --rm seaseq-clean
    ;;
    clean)

        echo "🚀 Running data cleanup...
        docker compose run --rm seaseq-clean
        ;;
        down)
        
        
        echo "🛑 Stopping all containers and removing volumes...    "
    echo "Usage: $0 {cli|api|both|down|clean} [args...]"
    ;;
esac
--- a/destroydata.sh            