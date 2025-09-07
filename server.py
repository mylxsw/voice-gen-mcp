#!/usr/bin/env python3
"""
MCP Server for Voice Generation using Minimax AI API.
Provides tools to generate speech from text and upload to S3.
"""

import os
import sys
import binascii
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from pathlib import Path

# Add parent directory to path to import voice generation modules
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

from fastmcp import FastMCP, Context
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Import voice generation components
from config import load_config
from voice_generator import VoiceGenerator, VoiceGeneratorError
from auth import create_auth_middleware, auth_required, AuthenticationError

# Configure logging to stderr (required for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("voice-gen")

# Global instances
voice_generator: Optional[VoiceGenerator] = None
s3_client: Optional[boto3.client] = None
config: Optional[Dict[str, Any]] = None
auth_middleware = None


def initialize_services():
    """Initialize the voice generator, S3 client, and authentication middleware with configuration."""
    global voice_generator, s3_client, config, auth_middleware
    try:
        config = load_config()
        voice_generator = VoiceGenerator(config)

        # Initialize S3 client
        s3_config = config.get('s3', {})
        s3_client = boto3.client(
            's3',
            region_name=s3_config['region'],
            aws_access_key_id=s3_config['access_key_id'],
            aws_secret_access_key=s3_config['secret_access_key'],
            endpoint_url=s3_config.get('endpoint_url', 'https://s3.amazonaws.com')
        )

        # Initialize authentication middleware
        auth_middleware = create_auth_middleware(config)
        if auth_middleware:
            logger.info("Authentication middleware initialized successfully")
        else:
            logger.info("Authentication is disabled")

        logger.info("Voice generator and S3 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


def upload_to_s3(audio_data: bytes, filename: str) -> str:
    """Upload audio data to S3 and return the public URL."""
    try:
        s3_config = config.get('s3', {})
        bucket_name = s3_config['bucket_name']
        prefix = s3_config.get('prefix', 'voice-gen/')
        public_url_base = s3_config.get('public_url_base', f'https://{bucket_name}.s3.{s3_config["region"]}.amazonaws.com')

        # Generate directory structure: Year/Month/Day_{unique_id}_{filename}
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        unique_id = str(uuid.uuid4())[:8]

        # Create S3 key with new format: prefix/Year/Month/Day_{unique_id}_{filename}
        s3_key = f"{prefix}{year}/{month}/{day}_{unique_id}_{filename}"

        # Calculate expiration date (1 month from now)
        expiration_date = now + timedelta(days=30)

        # Upload to S3 with expiration metadata
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=audio_data,
            ContentType='audio/mpeg',
            Metadata={
                'expiration-date': expiration_date.isoformat(),
                'created-date': now.isoformat(),
                'unique-id': unique_id
            },
            Expires=expiration_date
        )

        # Generate public URL
        public_url = f"{public_url_base}/{s3_key}"

        logger.info(f"Audio uploaded to S3: {s3_key} (expires: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')})")
        return public_url

    except ClientError as e:
        error_msg = f"S3 upload error: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except NoCredentialsError:
        error_msg = "S3 credentials not found"
        logger.error(error_msg)
        raise Exception(error_msg)


@auth_required(auth_middleware)
@mcp.tool
async def generate_voice(
    text: str,
    model: str = "speech-2.5-hd-preview",
    voice_id: str = "mylxsw_voice_1",
    ctx: Context = None
) -> str:
    """Generate speech audio from text using Minimax AI API and upload to S3.

    Args:
        text: The text to convert to speech
        model: Model to use for generation (default: speech-2.5-hd-preview)
        voice_id: Voice ID to use (default: mylxsw_voice_1)
        ctx: FastMCP context for logging and other operations

    Returns:
        str: Success message with S3 URL or error message
    """
    try:
        if ctx:
            await ctx.info(f"Starting voice generation for text: {text[:50]}...")

        if not voice_generator or not s3_client:
            initialize_services()

        if not text.strip():
            error_msg = "Error: Text cannot be empty"
            if ctx:
                await ctx.error(error_msg)
            return error_msg

        logger.info(f"Generating voice for text: {text[:50]}...")

        # Generate audio data
        audio_data = voice_generator.generate_voice(
            text=text,
            model=model,
            voice_id=voice_id
        )

        if ctx:
            await ctx.info("Voice generated successfully, uploading to S3...")

        # Generate filename (timestamp info is already in S3 path)
        filename = "voice.mp3"

        # Upload to S3
        public_url = upload_to_s3(audio_data, filename)

        file_size = len(audio_data)
        logger.info(f"Voice generated and uploaded successfully ({file_size} bytes)")

        if ctx:
            await ctx.info(f"File uploaded successfully: {public_url}")

        return f"Successfully generated voice audio and uploaded to S3.\nURL: {public_url}\nSize: {file_size} bytes"

    except AuthenticationError as e:
        error_msg = f"Authentication error: {e}"
        logger.error(error_msg)
        return error_msg
    except VoiceGeneratorError as e:
        error_msg = f"Voice generation error: {e}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Initialize services
    try:
        initialize_services()
        logger.info("MCP Voice Generation Server starting...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

    # Get server configuration
    transport_type = os.getenv('MCP_TRANSPORT', 'stdio')
    server_host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
    server_port = int(os.getenv('MCP_SERVER_PORT', '8000'))

    # Start the MCP server
    if transport_type == 'http':
        logger.info(f"Starting MCP server in HTTP mode on {server_host}:{server_port}")
        mcp.run(transport='http', host=server_host, port=server_port, path='/mcp')
    elif transport_type == 'sse':
        logger.info(f"Starting MCP server in SSE mode on {server_host}:{server_port}")
        mcp.run(transport='sse', host=server_host, port=server_port)
    else:
        logger.info("Starting MCP server in STDIO mode")
        mcp.run(transport='stdio')

