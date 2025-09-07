#!/usr/bin/env python3
"""
Voice generation module that handles communication with the Minimax AI API.
"""

import binascii
import json
import requests
from typing import Dict, Any, Optional


class VoiceGeneratorError(Exception):
    """Custom exception for voice generation errors."""
    pass


class VoiceGenerator:
    """Handles voice generation using the Minimax AI API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the VoiceGenerator with configuration.
        
        Args:
            config: Configuration dictionary containing API settings
        """
        self.config = config
        self.base_url = config['api']['base_url']
        self.group_id = config['api']['group_id']
        self.api_key = config['api']['api_key']
        self.audio_settings = config['audio_settings']
        self.defaults = config['defaults']
    
    def generate_voice(self, text: str, model: str = None, voice_id: str = None) -> bytes:
        """
        Generate voice audio from text.
        
        Args:
            text: The text to convert to speech
            model: The model to use (defaults to config value)
            voice_id: The voice ID to use (defaults to config value)
            
        Returns:
            bytes: The audio data in binary format
            
        Raises:
            VoiceGeneratorError: If there's an error during generation
        """
        if not text:
            raise VoiceGeneratorError("Text cannot be empty")
        
        # Use defaults if not provided
        model = model or self.defaults['model']
        voice_id = voice_id or self.defaults['voice_id']
        
        # Prepare API request
        url = f"{self.base_url}?GroupId={self.group_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._create_payload(text, model, voice_id)
        
        try:
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse the JSON response
            response_data = response.json()
            
            # Extract the hex-encoded audio data
            if "data" in response_data and "audio" in response_data["data"]:
                hex_audio = response_data["data"]["audio"]
                # Convert hex to binary
                return binascii.unhexlify(hex_audio)
            else:
                raise VoiceGeneratorError(f"Unexpected API response format: {response_data}")
                
        except requests.exceptions.RequestException as e:
            raise VoiceGeneratorError(f"Error making API request: {e}")
        except json.JSONDecodeError as e:
            raise VoiceGeneratorError(f"Error parsing API response: {e}")
        except binascii.Error as e:
            raise VoiceGeneratorError(f"Error decoding audio data: {e}")
    
    def _create_payload(self, text: str, model: str, voice_id: str) -> Dict[str, Any]:
        """
        Create the API request payload.
        
        Args:
            text: The text to convert to speech
            model: The model to use
            voice_id: The voice ID to use
            
        Returns:
            Dict[str, Any]: The request payload
        """
        return {
            "model": model,
            "text": text,
            "timber_weights": [
                {
                    "voice_id": voice_id,
                    "weight": 1
                }
            ],
            "voice_setting": {
                "voice_id": "",
                "speed": 1,
                "pitch": 0,
                "vol": 1,
                "latex_read": False
            },
            "audio_setting": {
                "sample_rate": self.audio_settings['sample_rate'],
                "bitrate": self.audio_settings['bitrate'],
                "format": self.audio_settings['format']
            },
            "language_boost": "auto"
        }