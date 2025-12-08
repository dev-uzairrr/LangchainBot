#!/bin/bash
# Script to upgrade packages to fix compatibility issues

echo "Upgrading packages to fix compatibility issues..."
echo ""

# Upgrade groq to latest version
echo "Upgrading groq..."
pip install --upgrade "groq>=0.9.0"

# Install transformers and torch (replacing sentence-transformers)
echo "Installing transformers and torch..."
pip install --upgrade "transformers>=4.35.0" "torch>=2.0.0"

# Install all requirements
echo "Installing/updating all requirements..."
pip install -r requirements.txt

echo ""
echo "Package upgrade complete!"
echo "You can now start the server with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

