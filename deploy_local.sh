#!/bin/bash

# Deploy local plugin to Claude Code cache for testing
# This script copies the current plugin to the latest version in local cache

set -e  # Exit on error

PLUGIN_NAME="video-creator"
MARKETPLACE_NAME="claude-video-plugin"
CACHE_BASE="$HOME/.claude/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME"

echo "🚀 Deploying plugin to local cache..."
echo ""

# Check if cache directory exists
if [ ! -d "$CACHE_BASE" ]; then
    echo "❌ Error: Plugin cache directory not found: $CACHE_BASE"
    echo "Please install the plugin first using: claude plugin install $PLUGIN_NAME@$MARKETPLACE_NAME"
    exit 1
fi

# Find the latest version directory
LATEST_VERSION=$(ls -1 "$CACHE_BASE" | sort -V | tail -n 1)

if [ -z "$LATEST_VERSION" ]; then
    echo "❌ Error: No version directories found in $CACHE_BASE"
    exit 1
fi

TARGET_DIR="$CACHE_BASE/$LATEST_VERSION"

echo "📂 Source: $(pwd)"
echo "📦 Target: $TARGET_DIR"
echo "🏷️  Version: $LATEST_VERSION"
echo ""

# Confirm deployment
read -p "Deploy to this location? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "📋 Copying files..."

# Copy directories
rsync -av --delete \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    --exclude='deploy_local.sh' \
    .claude-plugin/ "$TARGET_DIR/.claude-plugin/"

rsync -av --delete \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    commands/ "$TARGET_DIR/commands/"

# Copy scripts directory if exists
if [ -d "scripts" ]; then
    rsync -av --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='.DS_Store' \
        scripts/ "$TARGET_DIR/scripts/"
fi

# Copy README if exists
if [ -f "README.md" ]; then
    cp README.md "$TARGET_DIR/README.md"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployed files:"
ls -lh "$TARGET_DIR"
echo ""
echo "🔍 Commands available:"
ls -1 "$TARGET_DIR/commands/" | sed 's/\.md$//' | sed 's/^/  \/'"$PLUGIN_NAME"':/'
echo ""
echo "💡 Tip: The changes are now active. You can test the plugin immediately."
echo "   To make this permanent, commit and push to GitHub, then update the plugin."
