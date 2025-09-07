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

5. **Generate a secure API key**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
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
VOICE_GEN_API_BASE_URL=https://api.minimax.chat/v1/t2a_v2
VOICE_GEN_DEFAULT_MODEL=speech-2.5-hd-preview
VOICE_GEN_DEFAULT_VOICE_ID=mylxsw_voice_1
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

#### Authentication (Required)
```bash
MCP_AUTH_ENABLED=true
MCP_API_KEY=your-secure-mcp-api-key-here
MCP_AUTH_HEADER=Authorization
MCP_REQUIRE_AUTH_FOR_TOOLS=true
```

#### Audio Settings (Optional)
```bash
VOICE_GEN_AUDIO_SAMPLE_RATE=32000
VOICE_GEN_AUDIO_BITRATE=128000
VOICE_GEN_AUDIO_FORMAT=mp3
```

#### Server Configuration (Optional)
```bash
MCP_TRANSPORT=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
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

### MCP Client Configuration

#### Claude Desktop
Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "voice-gen-http": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer your-secure-mcp-api-key-here"
      }
    }
  }
}
```

#### Other MCP Clients
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

**Returns:**
- Success message with S3 URL and file size
- Error message if generation fails

**Example:**
```json
{
  "text": "Hello, this is a test of the voice generation system.",
  "model": "speech-2.5-hd-preview",
  "voice_id": "mylxsw_voice_1"
}
```

## File Organization

Generated audio files are organized in S3 with the following structure:
```
bucket-name/
└── voice-gen/
    └── YYYY/
        └── MM/
            └── DD_{unique_id}_voice.mp3
```

Files include metadata:
- Creation date
- Expiration date (30 days)
- Unique identifier

## Security

- **Authentication**: API key authentication is enabled by default
- **Secure Headers**: Supports standard `Authorization: Bearer` format
- **Environment Variables**: Sensitive data stored in environment variables
- **S3 Security**: Files have automatic expiration (30 days)

## Development

### Project Structure
```
voice-gen-mcp/
├── server.py              # Main MCP server
├── voice_generator.py     # Voice generation logic
├── config.py             # Configuration management
├── auth.py               # Authentication middleware
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── env.example          # Environment template
└── README.md           # This file
```

### Running Tests
```bash
# Add test commands here when tests are implemented
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify `MCP_API_KEY` is set correctly
   - Check that the API key matches in both server and client configuration

2. **S3 Upload Failures**
   - Verify S3 credentials and permissions
   - Check bucket name and region configuration
   - Ensure the bucket exists and is accessible

3. **Voice Generation Errors**
   - Verify Minimax API credentials
   - Check API quota and limits
   - Ensure the voice ID exists in your account

4. **Connection Issues**
   - Check firewall settings for the configured port
   - Verify the server is running and accessible
   - Check Docker port mapping if using containers

### Logs

#### Local Development
Logs are output to stderr and can be redirected:
```bash
python3 server.py 2> server.log
```

#### Docker
View container logs:
```bash
docker logs voice-gen-mcp
docker-compose logs -f
```

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration examples

## Changelog

### Version 1.0.0
- Initial release
- Voice generation with Minimax AI API
- S3 integration with automatic upload
- MCP protocol support
- Docker deployment support
- Authentication middleware
