# Docker 部署指南

## 快速开始

### 1. 构建镜像
```bash
docker build -t voice-gen-mcp .
```

### 2. 运行容器
```bash
# 使用环境变量
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

# 或使用 .env 文件
docker run -d \
  --name voice-gen-mcp \
  -p 8000:8000 \
  --env-file .env \
  voice-gen-mcp
```

### 3. 使用 Docker Compose
```bash
# 复制并配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# Voice Generation API Configuration
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

# MCP Authentication Configuration (enabled by default for security)
MCP_AUTH_ENABLED=true
MCP_API_KEY=your-secure-mcp-api-key-here
MCP_AUTH_HEADER=Authorization
MCP_REQUIRE_AUTH_FOR_TOOLS=true

# MCP Server Configuration (optional)
MCP_TRANSPORT=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
```

## 服务访问

- **MCP 端点**: http://localhost:8000/mcp
- **健康检查**: 容器会自动进行健康检查

## Claude Desktop 配置

在 Claude Desktop 的配置文件中添加：

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

**注意**: 鉴权默认启用（`MCP_AUTH_ENABLED=true`），需要在配置中添加 `headers` 字段包含 API Key。推荐使用标准的 `Authorization: Bearer` 格式。
