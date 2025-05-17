# Load environment variables from .env
set -a
source .env
set +a

# Change directory to backend
cd backend || exit

# Activate virtual environment
source .venv/bin/activate
