# Voice Generation MCP Server

A Model Context Protocol (MCP) server that provides voice generation capabilities using the Minimax AI API. This server converts text to speech and automatically uploads the generated audio files to Amazon S3 for easy access and sharing.

## Features

- **Text-to-Speech Generation**: Convert text to high-quality speech using Minimax AI's voice synthesis API
- **S3 Integration**: Automatically upload generated audio files to Amazon S3 with organized directory structure
- **MCP Protocol Support**: Full compatibility with Model Context Protocol for seamless integration with AI assistants
- **Authentication**: Built-in API key authentication for secure access
- **Multiple Transport Modes**: Support for HTTP, SSE, and STDIO transport protocols
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Configurable Audio Settings**: Customizable sample rate, bitrate, and format options

## Prerequisites

- Python 3.8 or higher
- Minimax AI API credentials
- Amazon S3 bucket and credentials
- (Optional) Docker and Docker Compose for containerized deployment

## Installation

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-gen-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual configuration values
   ```

### Docker Installation

1. **Build the Docker image**
   ```bash
   docker build -t voice-gen-mcp .
   ```

2. **Run with Docker Compose**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   docker-compose up -d
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example` with the following required variables:

#### Voice Generation API (Required)
```bash
VOICE_GEN_API_GROUP_ID=your_minimax_group_id
VOICE_GEN_API_KEY=your_minimax_api_key
```

#### S3 Configuration (Required)
```bash
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your_s3_access_key_id
S3_SECRET_ACCESS_KEY=your_s3_secret_access_key
S3_ENDPOINT=https://s3.amazonaws.com
S3_PREFIX=voice-gen/
```

## Usage

### Starting the Server

#### Local Development
```bash
python3 server.py
```

#### Docker
```bash
docker run -d \
  --name voice-gen-mcp \
  -p 8000:8000 \
  --env-file .env \
  voice-gen-mcp
```

#### Docker Compose
```bash
docker-compose up -d
```


#### MCP Clients
The server supports multiple transport modes:
- **HTTP**: `http://localhost:8000/mcp`
- **SSE**: `http://localhost:8000/sse`
- **STDIO**: Direct process communication

### Available Tools

#### `generate_voice`
Converts text to speech and uploads to S3.

**Parameters:**
- `text` (string, required): The text to convert to speech
- `model` (string, optional): Model to use (default: "speech-2.5-hd-preview")
- `voice_id` (string, optional): Voice ID to use (default: "mylxsw_voice_1")
- `speed` (float, optional): Speech speed (default: 1.0, typically 0.5-2.0)

**Returns:**
- Success message with S3 URL and file size
- Error message if generation fails

**Example:**
```json
{
  "text": "Hello, this is a test of the voice generation system.",
  "model": "speech-2.5-hd-preview",
  "voice_id": "mylxsw_voice_1",
  "speed": 1.2
}
```

**Speed Control:**
- `speed = 0.5`: Half speed (slower speech)
- `speed = 1.0`: Normal speed (default)
- `speed = 1.5`: 1.5x speed (faster speech)
- `speed = 2.0`: Double speed (very fast speech)

## License

[MIT License](LICENSE)
