#!/bin/bash

REPO_URL="https://github.com/hardik-raina/IDesignSpec-Comparison.git" 
REPO_DIR="IDesignSpec-Comparison" 

echo "Cloning repository from $REPO_URL..."
git clone "$REPO_URL"

cd "$REPO_DIR" || { echo "Repository directory not found!"; exit 1; }

echo "Creating virtual environment 'comp'..."
python3 -m venv comp

echo "Activating virtual environment..."
source comp/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Deactivating virtual environment..."
deactivate

echo "Setup complete!"
