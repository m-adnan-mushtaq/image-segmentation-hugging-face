#! /bin/bash

# Logging function
log() {
  echo "[`date +"%Y-%m-%d %H:%M:%S"`] $1"
}

# Validate .env exists in the server directory
if [ ! -f server/.env ]; then
  log "ERROR: server/.env file not found!"
  exit 1
else
  log "server/.env found."
fi

# start server
log "Starting server setup..."
cd server
if [ ! -d venv ]; then
  log "Creating Python virtual environment..."
  python -m venv venv
else
  log "Using existing Python virtual environment."
fi
source venv/bin/activate
log "Installing Python dependencies..."
pip install -r requirements.txt

log "Launching server with Uvicorn..."
uvicorn main:app --reload &

# Give server a few seconds to start
sleep 3

# start client
cd ../client
log "Installing Node.js dependencies..."
npm install

log "Starting client development server..."
npm run dev