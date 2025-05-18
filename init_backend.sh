# Load environment variables from .env
set -a
source .env
set +a

docker-compose up -d

# Change directory to backend
cd backend || exit

# Activate virtual environment
source .venv/bin/activate
