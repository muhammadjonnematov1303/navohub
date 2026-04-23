#!/bin/bash
# Render build script

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Creating data directory..."
mkdir -p data

echo "✅ Build complete!"
