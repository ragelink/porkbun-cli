#!/bin/bash
set -e

# Script to build and run the Porkbun CLI Docker image with local .env file
# Usage: ./docker-bootstrap.sh [COMMAND] [ARGS...]
# Example: ./docker-bootstrap.sh domains list

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${BLUE}No .env file found. Creating a sample .env file...${NC}"
    cp .env.example .env
    echo -e "${BLUE}Please edit .env file with your credentials before running this script again.${NC}"
    exit 1
fi

echo -e "${GREEN}Building Docker image...${NC}"
docker build -t porkbun-cli .

echo -e "${GREEN}Running Porkbun CLI with local .env file...${NC}"

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    echo -e "${BLUE}No command specified. Running with --help:${NC}"
    docker run --rm \
        --env-file .env \
        -v "$(pwd):/app" \
        porkbun-cli --help
else
    echo -e "${BLUE}Running command: $@${NC}"
    docker run --rm \
        --env-file .env \
        -v "$(pwd):/app" \
        porkbun-cli "$@"
fi 