# Docker Deployment

## Quick Start

### 1. Build the image
```bash
docker build -t voice-gen-mcp .
```

### 2. Run the container
```bash
# Use environment variables
docker run -d \
  --name voice-gen-mcp \
  -p 8000:8000 \
  -e VOICE_GEN_API_GROUP_ID=your_group_id \
  -e VOICE_GEN_API_KEY=your_api_key \
  -e S3_BUCKET_NAME=your_bucket \
  -e S3_REGION=us-east-1 \
  -e S3_ACCESS_KEY_ID=your_access_key \
  -e S3_SECRET_ACCESS_KEY=your_secret_key \
  voice-gen-mcp

# Or use .env file
docker run -d \
  --name voice-gen-mcp \
  -p 8000:8000 \
  --env-file .env \
  voice-gen-mcp
```

### 3. Use Docker Compose
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env file, fill in your configuration

# Start the service
docker-compose up -d

# View the logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Environment Variable Configuration

Create `.env` file and configure the following variables:

```bash
# Voice Generation API Configuration (REQUIRED)   
VOICE_GEN_API_GROUP_ID=your_minimax_group_id
VOICE_GEN_API_KEY=your_minimax_api_key
VOICE_GEN_API_BASE_URL=https://api.minimax.chat/v1/t2a_v2
VOICE_GEN_DEFAULT_MODEL=speech-2.5-hd-preview
VOICE_GEN_DEFAULT_VOICE_ID=mylxsw_voice_1
VOICE_GEN_AUDIO_SAMPLE_RATE=32000
VOICE_GEN_AUDIO_BITRATE=128000
VOICE_GEN_AUDIO_FORMAT=mp3

# S3 Configuration
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your_s3_access_key_id
S3_SECRET_ACCESS_KEY=your_s3_secret_access_key
S3_ENDPOINT=https://s3.amazonaws.com
S3_PREFIX=voice-gen/
S3_PUBLIC_URL_BASE=

# MCP Server Configuration (optional)
MCP_TRANSPORT=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
```

