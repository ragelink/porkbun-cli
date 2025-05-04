#!/bin/bash
set -e

# Porkbun CLI Docker proxy script
# This script acts as a proxy to run the Porkbun CLI through Docker
# Usage: ./porkbun.sh [COMMAND] [ARGS...]
# Example: ./porkbun.sh domains list-all

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Docker volume name for persistent configuration
VOLUME_NAME="porkbun-cli-config"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${BLUE}No .env file found. Creating a sample .env file...${NC}"
    cp .env.example .env
    echo -e "${BLUE}Please edit .env file with your credentials before running this script again.${NC}"
    exit 1
fi

# Force rebuild flag
REBUILD=false
# Debug mode
DEBUG=false
# Reset config
RESET_CONFIG=false

# Parse arguments for special flags
while [[ "$1" == --* ]]; do
    case "$1" in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --reset-config)
            RESET_CONFIG=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Handle volume creation/reset
if [ "$RESET_CONFIG" = true ]; then
    echo -e "${YELLOW}Removing and recreating config volume...${NC}"
    docker volume rm "$VOLUME_NAME" 2>/dev/null || true
    docker volume create "$VOLUME_NAME"
elif ! docker volume inspect "$VOLUME_NAME" &>/dev/null; then
    echo -e "${BLUE}Creating Docker volume for persistent configuration...${NC}"
    docker volume create "$VOLUME_NAME"
fi

# Build the Docker image if it doesn't exist yet or if rebuild is requested
if ! docker image inspect porkbun-cli &>/dev/null || [ "$REBUILD" = true ]; then
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t porkbun-cli --no-cache .
fi

# Extract API credentials from .env file
if grep -q "PORKBUN_API_KEY" .env && grep -q "PORKBUN_SECRET_API_KEY" .env; then
    API_KEY=$(grep "PORKBUN_API_KEY" .env | cut -d'=' -f2- | tr -d ' ' | tr -d '"' | tr -d "'")
    SECRET_KEY=$(grep "PORKBUN_SECRET_API_KEY" .env | cut -d'=' -f2- | tr -d ' ' | tr -d '"' | tr -d "'")
    
    if [ -n "$API_KEY" ] && [ -n "$SECRET_KEY" ]; then
        echo -e "${GREEN}Using API credentials from .env file${NC}"
    else
        echo -e "${YELLOW}Warning: API credentials found in .env file but they appear to be empty.${NC}"
    fi
else
    echo -e "${YELLOW}Warning: No API credentials found in .env file.${NC}"
    API_KEY=""
    SECRET_KEY=""
fi

# Debug info
if [ "$DEBUG" = true ]; then
    echo -e "${BLUE}Debug: API_KEY length: ${#API_KEY}${NC}"
    echo -e "${BLUE}Debug: SECRET_KEY length: ${#SECRET_KEY}${NC}"
fi

# Create the Docker entry script that will handle profile setup
ENTRY_SCRIPT=$(mktemp)
cat > "$ENTRY_SCRIPT" << EOF
#!/bin/bash
set -e

# Create proper .porkbun directory structure
mkdir -p /root/.porkbun/profiles

# Debug output
if [ "\$DEBUG" = "true" ]; then
    echo "Config directory structure before setup:"
    ls -la /root/.porkbun/
    ls -la /root/.porkbun/profiles/ 2>/dev/null || echo "No profiles directory yet"
fi

# Setup the profile if it doesn't exist or we're forcing a reset
if [ ! -f /root/.porkbun/profiles/default.json ] || [ "\$RESET_CONFIG" = "true" ]; then
    echo "Setting up default profile with credentials from environment"
    
    # Create proper config.json file structure
    cat > /root/.porkbun/config.json << CONFIG
{
  "profiles": {
    "default": {
      "api_key": "\$PORKBUN_API_KEY",
      "secret_key": "\$PORKBUN_SECRET_API_KEY",
      "base_url": "https://porkbun.com/api/json/v3",
      "default": true
    }
  },
  "current_profile": "default"
}
CONFIG
    
    # Also create the individual profile file for compatibility
    cat > /root/.porkbun/profiles/default.json << PROFILE
{
    "api_key": "\$PORKBUN_API_KEY",
    "secret_key": "\$PORKBUN_SECRET_API_KEY",
    "base_url": "https://porkbun.com/api/json/v3"
}
PROFILE

    # Set default profile
    echo "default" > /root/.porkbun/default_profile
fi

# Debug output
if [ "\$DEBUG" = "true" ]; then
    echo "Config directory structure after setup:"
    ls -la /root/.porkbun/
    echo "Profile directory contents:"
    ls -la /root/.porkbun/profiles/
    echo "Config.json content:"
    cat /root/.porkbun/config.json || echo "No config.json file"
    echo "Default profile content:"
    cat /root/.porkbun/default_profile || echo "No default profile set"
    echo "Default profile JSON:"
    cat /root/.porkbun/profiles/default.json || echo "No default profile JSON"
fi

# Set permissions to ensure the profile is readable
chmod -R 755 /root/.porkbun

# Set environment variables for backup method
export PORKBUN_API_KEY="\$PORKBUN_API_KEY"
export PORKBUN_SECRET_KEY="\$PORKBUN_SECRET_API_KEY"

# Run the CLI command
if [ \$# -eq 0 ]; then
    exec python -m porkbun.cli --help
else
    exec python -m porkbun.cli "\$@"
fi
EOF

chmod +x "$ENTRY_SCRIPT"

if [ "$DEBUG" = true ]; then
    echo -e "${BLUE}Debug: Entry script:${NC}"
    cat "$ENTRY_SCRIPT"
fi

# Check if any arguments were provided
echo -e "${GREEN}Running Porkbun CLI with Docker...${NC}"
echo -e "${YELLOW}Note: If you encounter 403 Forbidden errors, please verify:${NC}"
echo -e "${YELLOW}1. Your API keys are correct in the .env file${NC}"
echo -e "${YELLOW}2. Your IP address is allowed in the Porkbun API settings${NC}" 
echo -e "${YELLOW}3. The API is enabled for each domain you're trying to manage${NC}"

docker run --rm \
    -it \
    -v "$(pwd):/app" \
    -v "$VOLUME_NAME:/root/.porkbun" \
    -v "$ENTRY_SCRIPT:/entry.sh" \
    -e DEBUG="$DEBUG" \
    -e RESET_CONFIG="$RESET_CONFIG" \
    -e PORKBUN_API_KEY="$API_KEY" \
    -e PORKBUN_SECRET_API_KEY="$SECRET_KEY" \
    -e LOGURU_LEVEL="DEBUG" \
    --entrypoint="/entry.sh" \
    porkbun-cli "$@"

# Clean up
rm -f "$ENTRY_SCRIPT" 