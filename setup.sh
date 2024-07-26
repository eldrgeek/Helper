#!/bin/bash

# Exit on error
set -e

echo "Setting up the project..."

# Install root dependencies
echo "Installing root dependencies..."
npm install

# Install client dependencies
echo "Installing client dependencies..."
cd client
npm install
cd ..

# Install server dependencies
echo "Installing server dependencies..."
cd server
npm install
cd ..

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Run Python configuration script
echo "Running Python configuration script..."
python @conf.py

echo "Setup complete!"